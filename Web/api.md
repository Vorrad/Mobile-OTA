# 接口定义文件

格式样例：
```
## primary

### 函数接口1

Primary.update_cycle(param x, param y): 用于周期性验证升级

#### param x

参数x，类型XXX，用途XXX，用法XXX

#### param y
 
...

### 函数接口2

Primary.clean_slate():...

...

### 目录与全局变量

WORKING_DIR/temp_primary/

- 保存primary元数据的目录

WORKING_DIR/temp_primary/secondary1/

- 保存secondary1的元数据目录

param x

- 类型XXX，用途XXX，用法XXX

...
```

## keys

### 数据结构定义

公钥`*.pub`

- 类型：字典
- 结构：

```
{
 "keyid_hash_algorithms": ["sha256", "sha512"],
 "keyval": {"public": "99ef8790687ca252c4677a80a34e401efb7e17ccdf9b0fcb5f1bc3260c432cb9"}, 
 "keytype": "ed25519"
}
```

## demo_primary

### 函数接口1

demo_primary.clean_slate(use_new_keys, vin, ecu_serial)

> ### 作用
> 1. 初始化客户端目录
> 2. 从director、image库中拷贝元数据
> 3. 初始化一个Primary ECU实例
> 4. 尝试向director注册ECU序列号和公钥
> 5. ECU生成一份含有所有ECU版本清单的车辆版本清单并签名，其格式符合`uptane.formats.VEHICLE_VERSION_MANIFEST_SCHEMA`
> 6. 向director上传该车辆版本清单

#### use_new_keys

是否使用新密钥（默认等于`False`），如果使用则为primary生成新密钥

#### vin

车辆识别码

在demo中默认等于`_vin`，值为 `"democar"`。如不采用默认值，则`_vin`根据输入的`vin`更新

#### ecu_serial

primary ecu 序列号

在demo中默认等于`_ecu_serial`，值为 `"INFOdemocar"`。如不采用默认值，则`_ecu_serial`根据输入的`ecu_serial`更新

### 目录与全局变量

`CLIENT_DIRECTORY`

- 客户端目录完整路径

`CLIENT_DIRECTORY_PREFIX`

- demo中定义为`"temp_primary"`
- 客户端目录相对路径
- 在生成时后面会附带5位随机字符

`pinned.json_primary_`

## Primary（类）

[原文](./api-primary.md)

### 构造函数

参数列表：

#### full_client_dir

客户端绝对路径

#### director_repo_name

director库名，默认为`"director"`

pinning文件中必须有记录
    
#### vin

#### ecu_serial

#### primary_key

ecu的密钥，格式符合`tuf.formats.ANYKEY_SCHEMA`

#### time

#### timeserver_public_key

用于验证timeserver签名的公钥

#### my_secondaries

可选

secondaries的列表
