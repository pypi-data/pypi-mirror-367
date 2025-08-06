from libs.call_context_lib.base import BaseCallContext
import json
import asyncio

from libs.call_context_lib.core import CallContextCallback


class MQExperimentLogger(CallContextCallback):
    def __init__(self, topic: str):
        self.topic = topic
        # self.producer = YourMQProducer(...)  # 실제 MQ 프로듀서 연동이 필요할 경우

    async def call(self, ctx: BaseCallContext):
        experiment_id = ctx.get_meta("experiment_id")
        if not experiment_id:
            return  # 실험 정보 없으면 로그 생략

        # Safely include all meta data in the payload
        meta_data = {}
        if hasattr(ctx, 'meta') and ctx.meta is not None:
            try:
                # Convert meta data to a JSON-serializable format
                meta_data = {
                    str(k): str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v
                    for k, v in ctx.meta.items()
                }
            except (AttributeError, TypeError) as e:
                print(f"[WARNING] Failed to process meta data: {e}")
        
        payload = {
            "turn_id": ctx.get_turn_id(),
            "user_id": ctx.get_user_id(),
            **meta_data  # Include processed meta data
        }

        # MQ로 전송하는 부분 (예시: asyncio.Queue, Kafka, NATS 등)
        print(f"[MQExperimentLogger] topic={self.topic} payload={json.dumps(payload)}")

        # 예시로 asyncio.sleep()만 넣음
        await asyncio.sleep(0.001)

        # 실제 사용 예:
        # await self.producer.send(self.topic, value=payload)