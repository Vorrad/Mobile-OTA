
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

### 目录与全局变量

`CLIENT_DIRECTORY`

- 客户端目录完整路径

`CLIENT_DIRECTORY_PREFIX`

- demo中定义为`"temp_primary"`
- 客户端目录相对路径
- 在生成时后面会附带5位随机字符

`pinned.json_primary_<5位随机字符>`

- primary的pinned文件，保存存储库信息

### demo_primary.clean_slate(use_new_keys=False, vin, ecu_serial)

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

### demo_primary.update_cycle()

> ### 作用
> 1. 产生nonce并发送给timeserver，从timeserver获取时间
> 2. 更新ECU时间
> 3. 更新ECU的元数据，并从director、image库下载安装包
> 
>   `Primary.primary_update_cycle()`
> 4. ECU生成一份含有所有ECU版本清单的车辆版本清单并签名，其格式符合`uptane.formats.VEHICLE_VERSION_MANIFEST_SCHEMA`
> 5. 向director上传该车辆版本清单

#### exception

`bad Timestamp metadata`

- director请求安装一个比ECU时间戳更早的时间戳，该请求将不被执行

## Primary（类）

[原文](./api-primary.md)

### 目录与全局变量

`nonce`

- Secondary产生的一段随机数，被用于发送给timeserver，timeserver收到后会对其进行签名并返回一个时间戳
- Secondary可以通过比对nonce认证服务器

### 构造函数__init__(...)

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

## demo_director

### demo_director.clean_slate()
director 主进程 包括创建 director 目录以及写入ECU信息
### demo_director.write_to_live()
把每个车辆目录的元数据进行写入和存放到仓库中
### demo_director.backup_repositories()
备份函数 备份最后一次写入状态 默认全部备份(可选：车辆识别码进行备份)
### demo_director.restore_repositories()
存放最后备份的 director 内容 
元数据从 '{repo_dir}/metadata.backup' 存储到

    '{repo_dir}/metadata.staged' 

    and '{repo_dir}/metadata'
### demo_revoke_compromised_keys()

撤销现有的时间戳、快照、keys

并为每辆车生成新的keys

director 服务也会更新

### demo_director.sign_with_compromised_keys_attack(vin=None):
在攻击状态下，为所有车辆重新生成keys 并对之前的元数据进行签名。
用来防止攻击(大概...)


### demo_director.undo_sign_with_compromised_keys_attack(vin=None):
撤销sign_with_compromised_keys_attack(vin=None)的操作，恢复到之前的服务状态

### demo_director.add_target_to_director(target_fname, filepath_in_repo, vin, ecu_serial):
用于更具体演示

需要指定如下内容：

    根目录 
    所要添加的目录 
    ecu_serial

### demo_director.add_target_and_write_to_live(filename, file_content, vin, ecu_serial):
add_target_to_director的高级版本，加入write_to_live操作

### demo_director.host()
将 director 作为单独进程托管到http上
>使用demo_director.kill_server()停止

>使用demo_director.listen()来启动服务

>若已有服务则不会启动任何进程

### demo_director.listen()
启动 director 服务端口监听

    submit_vehicle_manifest

    register_ecu_serial
>必须使用demo_director.host()来通过http提供元数据

### demo_director.mitm_arbitrary_package_attack(vin, target_filepath)以及demo_director.undo_mitm_arbitrary_package_attack(vin, target_filepath):

模拟以及撤销中间人攻击 director库

### demo_director.backup_timestamp(vin):以及 demo_director.replay_timestamp(vin):

拷贝以及回滚之前的时间戳

### demo_director.restore_timestamp(vin):
将replay_timestamp记录的current_timestamp_backup移动到timestamp并存储(?)

### demo_director.prepare_replay_attack_nokeys(vin):
重放攻击的预先准备

### demo_director.replay_attack_nokeys(vin)和demo_director.undo_replay_attack_nokeys(vin):
重放攻击实施以及撤销
### demo_director.keyed_arbitrary_package_attack(vin, ecu_serial, target_filepath)和director.undo_keyed_arbitrary_package_attack(vin, ecu_serial, target_filepath):
添加恶意ECU目标攻击以及撤销

### demo_director.clear_vehicle_targets(vin):
从 director中删除指定车辆的命令，以便重新分配任务

### demo_director.kill_server():
关闭http服务，但不影响director 继续服务

## uptane/services/director
### 参数列表
    irector_repos_dir,
    key_root_pri,
    key_root_pub,
    key_timestamp_pri,
    key_timestamp_pub,
    key_snapshot_pri,
    key_snapshot_pub,
    key_targets_pri,
    key_targets_pub
### director.register_ecu_serial(self, ecu_serial, ecu_key, vin, is_primary=False):
主要用于密钥验证将self与ecu_serial和ecu_key验证

### director.validate_ecu_manifest(self, ecu_serial, signed_ecu_manifest):
用于检验signed_ecu_manifest是否匹配

### director.register_vehicle_manifest(self, vin, primary_ecu_serial, signed_vehicle_manifest):
将ECU数据保存在InventoryDB中
只有在主服务器的签名无效情况才会报错
单个ECU无效则只会对其丢弃并警告

### director.validate_primary_certification_in_vehicle_manifest(self, vin, primary_ecu_serial, vehicle_manifest):
对primary_ecu_serial进行验证

### director.register_ecu_manifest(self, vin, ecu_serial, signed_ecu_manifest):
检验后对ecu信息进行登记 
    调用 validate_ecu_manifest

### director.add_new_vehicle(self, vin, primary_ecu_serial=None):
将新车辆添加到inventoryDB中

### director.create_director_repo_for_vehicle(self, vin):
配合 director.add_new_vehicle
### director.add_target_for_ecu(self, vin, ecu_serial, target_filepath):
为ECU分配升级任务

--------------------

## demo_primary

### 无接口

>主要功能：充当符合 Uptane 的时间服务器：
>
>1.通过 XML-RPC 侦听来自车辆的请求。
>
>2.接收随机数列表并以列出这些随机数的签名时间证明作为响应

[主要函数](./api-timeserver.md)
