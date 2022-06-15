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