from atguigu.domain.state import DialogueState
from atguigu.plan.turn_plan import ClarifyReason


class ClarifyResponder:
    async def respond(self,
                      reason:ClarifyReason,
                      dialogue_state:DialogueState):
        pass
