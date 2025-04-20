from enum import Enum
from typing import List

class SymbolOutputSection(str, Enum):
    """
    WHAT: 定義符號輸出區段的類型
    WHY: 確保符號區段類型的一致性和有效性
    """
    CODE = "code"
    DATA = "data"
    INIT = "init"
    ALWAYS_POWER_ON = "always_power_on"
    RO_AFTER_WRITE = "ro_after_write"

def validate_output_section(section: str) -> bool:
    """
    WHAT: 驗證輸出區段是否為有效值
    WHY: 確保資料完整性
    """
    return section in [item.value for item in SymbolOutputSection]

def get_output_section_description(section: str) -> str:
    """
    WHAT: 獲取輸出區段的描述
    WHY: 提供人類可讀的區段說明
    """
    descriptions = {
        SymbolOutputSection.CODE.value: "程式碼區段",
        SymbolOutputSection.DATA.value: "資料區段",
        SymbolOutputSection.INIT.value: "初始化區段",
        SymbolOutputSection.ALWAYS_POWER_ON.value: "永遠保持供電的區段",
        SymbolOutputSection.RO_AFTER_WRITE.value: "寫入後唯讀區段"
    }
    return descriptions.get(section, "未知區段")
