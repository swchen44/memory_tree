# 背景為資料為 bare-metal 的 riscv elf , compiled from clang/llm, 
- symbol 會被配置到不同的physical memory， 包含 sysram, ilm, dlm, ext memory1, ext memory2, 加入起約為3000kbytes, 
- 每physical memory段有自己的起點和最大size, 
- 每個 physical memory 成本不同，ilm/dlm 是最貴速度最快(成本數值10)，sysram 是中等(成本數值8)，ext memory1, ext memory2 是最便宜(成本數值2)
- 每個module 包含多個symbol, 分配到不同physical memory, 
- module的成本是多個symbol 組合，而symbol 成本會被分配的phsical memory 來計算
- 利用多種可視化圖，找出目前成本最高的module 和symbol, 作重點分析



# symbol (像之前員工）strucutre如下 
- 有symbol name
- symbol input section (code/data/bss) 
- symbol address ( 32bit address , hex format) 
- symbol size (單位byte) 
- symbol protection(ro/rw/ro after write/always power on) 
- symbol out section (sysram data, sysram code, ilm, dlm, ilm_always_power_on, dlm_always_power_on, ext memory1 code, ext memory1 data, external , ext memory2 code, ext memory2 data ) 
- symbol physical memory (sysram, ilm, dlm, ext memory1, ext memory2) 
- symbol realtime (Yes/No)
- symbol filename, 
- symbol module name

# 資料階層 由粗排到細
## 統計階層
- physical memory
- symbol out section
- module 
- filename
- symbol (會被分配在不同physical memory)

## module 由file 組合，file 由symbol 組合

## 跨physical memory階層
- module
- filename




