import docker
import redis
import random
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
import atexit
import logging
import os
import json
import threading
import time

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ContainerManager')

# Docker客户端
docker_client = docker.from_env()

# Redis用于会话和容器池管理
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# 调度器
scheduler = BackgroundScheduler()
scheduler.start()
atexit.register(lambda: scheduler.shutdown())


class ContainerPoolManager:
    def __init__(self, image_name, pool_size=10, base_port=7000, runtime="runc", attach_ports={}, attach_environments={}, attach_volumes={}):
        self.image_name = image_name
        self.base_port = base_port
        self.runtime = runtime
        self.attach_ports = attach_ports
        self.attach_environments = attach_environments
        self.attach_volumes = attach_volumes
        self.used_ports = set()
        self.pool_size = pool_size
        self.lock = threading.Lock()
        self.initialize_pool()

    def initialize_pool(self):
        """初始化容器池"""
        logger.info(f"Initializing container pool with {self.pool_size} containers")
        if redis_client.llen('container_pool') == 0:
            for i in range(self.pool_size):
                container_info = self.create_container()
                if container_info:
                    redis_client.rpush('container_pool', json.dumps(container_info))
                    logger.info(f"Created container {container_info['id']} on port {container_info['port']}")

    def get_available_port(self):
        """获取可用端口"""
        while True:
            port = random.randint(self.base_port, self.base_port + 1000)
            if port not in self.used_ports:
                self.used_ports.add(port)
                return port

    def create_container(self):
        """创建单个容器"""
        try:
            container_port = self.get_available_port()

            container = docker_client.containers.run(
                image=self.image_name,
                detach=True,
                runtime=self.runtime,
                ports=self.attach_ports,
                environment=self.attach_environments,
                volumes=self.attach_volumes,
                restart_policy={"Name": "unless-stopped"},
                remove=False,
            )

            # 等待容器启动
            time.sleep(5)

            # 返回容器信息
            return {
                'id': container.id,
                'port': container_port,
                'created_at': str(datetime.now())
            }
        except docker.errors.APIError as e:
            logger.error(f"Docker API error creating container: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating container: {e}")
            return None

    def get_container_from_pool(self):
        """从池中获取一个容器"""
        with self.lock:
            container_data = redis_client.lpop('container_pool')
            if container_data:
                return json.loads(container_data)
            return None

    def assign_container_to_user(self):
        """分配容器给用户并设置销毁时间"""
        # 从池中获取容器
        container_info = self.get_container_from_pool()

        if not container_info:
            # 池为空则创建新容器
            logger.warning("Container pool empty, creating new container")
            container_info = self.create_container()
            if not container_info:
                return None, None

        # 记录用户容器分配
        assigned_time = datetime.now()
        expire_time = assigned_time + timedelta(hours=1)
        # 设置销毁任务
        self.schedule_container_destruction(
            container_info['id'],
            container_info['port'],
            expire_time
        )

        # 设置容器创建任务
        create_time = assigned_time + timedelta(minutes=1)
        self.schedule_container_creation(
            create_time
        )

        logger.info(f"Assigned container {container_info['id']}, will expire at {expire_time}")

        return container_info['id'], container_info['port']

    def schedule_container_creation(self, create_time):
        """调度容器创建任务"""
        job_id = time.time()
        scheduler.add_job(
            func=self.create_push_container,
            trigger=DateTrigger(run_date=create_time),
            args=[job_id],
            id=f"creation_{job_id}",
            replace_existing=True
        )
        logger.info(f"Scheduled creation for container creation_{job_id} at {create_time}")

    def schedule_container_destruction(self, container_id, port, expire_time):
        """调度容器销毁任务"""
        scheduler.add_job(
            func=self.destroy_container,
            trigger=DateTrigger(run_date=expire_time),
            args=[container_id, port],
            id=f"destroy_{container_id}",
            replace_existing=True
        )
        logger.info(f"Scheduled destruction for container {container_id} at {expire_time}")

    def create_push_container(self, job_id):
        # 创建新容器加入池中
        new_container = self.create_container()
        if new_container:
            redis_client.rpush('container_pool', json.dumps(new_container))
            logger.info(f"create container with {new_container['id']}")
        else:
            logger.error("Failed to create container...")

        # 移除调度任务
        try:
            scheduler.remove_job(f"creation_{job_id}")
        except:
            pass

    def destroy_container(self, container_id, port):
        """销毁容器并创建新容器补充池"""
        try:

            # 销毁旧容器
            try:
                container = docker_client.containers.get(container_id)
                container.stop(timeout=5)
                container.remove(force=True)
                logger.info(f"Stopped container {container_id}")
            except docker.errors.NotFound:
                logger.warning(f"Container {container_id} not found during destruction")

            # 释放端口
            self.used_ports.discard(port)

            # 创建新容器加入池中
            # new_container = self.create_container()
            # if new_container:
            #     redis_client.rpush('container_pool', json.dumps(new_container))
            #     logger.info(f"Replaced container {container_id} with {new_container['id']}")
            # else:
            #     logger.error("Failed to create replacement container")

            # 移除调度任务
            try:
                scheduler.remove_job(f"destroy_{container_id}")
            except:
                pass
        except Exception as e:
            logger.error(f"Error during container destruction/replacement: {e}")