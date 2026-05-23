from astrbot.api.event import AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api.event.filter import llm_tool
import logging

logger = logging.getLogger("astrbot")

@register("cmd_bridge", "夕小柠 & 陆渊", "指令转发桥接器：允许 LLM 自主执行系统指令", "1.2.0")
class CmdBridge(Star):
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.config = config

    @llm_tool(name="execute_plugin_command")
    async def execute_plugin_command(self, event: AstrMessageEvent, command: str):
        """
        自主执行系统或插件指令。
        
        Args:
            command (string): 完整的指令字符串，例如 "/hapi list" 或 "/status"。
        """
        # 获取管理员列表
        admin_list = [x.strip() for x in str(self.config.get("admin_qqs", "1591793025")).split(",") if x.strip()]
        
        sender_id = str(event.get_sender_id())

        # 如果是管理员，直接放行
        if sender_id in admin_list:
            is_allowed = True
        else:
            # 否则，检查白名单
            allowed_str = self.config.get("allowed_prefixes", "/hapi, /echo, /status")
            allowed = [p.strip() for p in allowed_str.split(",") if p.strip()]
            is_allowed = False
            for prefix in allowed:
                if command.startswith(prefix):
                    is_allowed = True
                    break
        
        if not is_allowed:
            return f"错误：指令 '{command}' 不在白名单内，且您不是管理员。"
        
        try:
            # 核心逻辑：模拟发送指令并注入回系统
            # 注意：这里需要确保 command 是以指令前缀（如 /）开头的
            cmd_str = command if command.startswith("/") else f"/{command}"
            
            # 使用标准的 handle_event 重新注入指令
            # 我们通过 event.instantiate_event 创建一个模拟的新事件
            new_event = event.instantiate_event(cmd_str)
            await self.context.handle_event(new_event)
            
            logger.info(f"[CmdBridge] 已成功转发指令: {cmd_str}")
            return f"✅ 指令已执行：{cmd_str}。请查看后续消息反馈。"
        except Exception as e:
            logger.error(f"[CmdBridge] 指令转发失败: {e}")
            return f"❌ 执行出错: {str(e)}"
