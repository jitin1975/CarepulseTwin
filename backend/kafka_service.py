import json
from aiokafka import AIOKafkaProducer,AIOKafkaConsumer
from backend.config import settings
class KafkaService:
 async def start(self):
  self.producer=AIOKafkaProducer(bootstrap_servers=settings.kafka_bootstrap,value_serializer=lambda v:json.dumps(v,default=str).encode());await self.producer.start()
 async def publish(self,e):await self.producer.send_and_wait(settings.kafka_topic,e)
 async def stop(self):
  if getattr(self,'producer',None):await self.producer.stop()
 async def consume(self,handler):
  c=AIOKafkaConsumer(settings.kafka_topic,bootstrap_servers=settings.kafka_bootstrap,group_id='carepulse-backend',auto_offset_reset='latest',value_deserializer=lambda v:json.loads(v.decode()));await c.start()
  try:
   async for m in c:await handler(m.value)
  finally:await c.stop()
