## 一、image

### 1.  clean_slate(use_new_keys=False): 

a. 设置image库默认路径

```
  if os.path.exists(demo.IMAGE_REPO_TARGETS_DIR):
    shutil.rmtree(demo.IMAGE_REPO_TARGETS_DIR)    //如果路径存在，全部删除

  os.makedirs(demo.IMAGE_REPO_TARGETS_DIR)        //创建目录 
```

b. 在./repomain下创建image库

```
repo = rt.create_new_repository(demo.IMAGE_REPO_NAME)

// API
// tuf.repository_tool库中rt.create_new_repository(demo.IMAGE_REPO_NAME)
```

c.产生相关密钥，保存在demo/keys/目录下

```
  if use_new_keys:
    demo.generate_key('mainroot')
    demo.generate_key('maintimestamp')
    demo.generate_key('mainsnapshot')
    demo.generate_key('maintargets')
    demo.generate_key('mainrole1')

  key_root_pub = demo.import_public_key('mainroot')
  key_root_pri = demo.import_private_key('mainroot')
  key_timestamp_pub = demo.import_public_key('maintimestamp')
  key_timestamp_pri = demo.import_private_key('maintimestamp')
  key_snapshot_pub = demo.import_public_key('mainsnapshot')
  key_snapshot_pri = demo.import_private_key('mainsnapshot')
  key_targets_pub = demo.import_public_key('maintargets')
  key_targets_pri = demo.import_private_key('maintargets')
  key_role1_pub = demo.import_public_key('mainrole1')     //暂时未用到
  key_role1_pri = demo.import_private_key('mainrole1')
  
  // API
  // demo中_ init _.py 中包含：
  // demo.generate_key(keyname)
  // demo.import_public_key(keyname)
  // demo.import_private_key(keyname)
  // 本质上是对tuf库tuf.repository_tool的调用：
  // rt.generate_and_write_ed25519_keypair(
      os.path.join(DEMO_KEYS_DIR, keyname), password='pw')r
  // rt.import_ed25519_publickey_from_file(
      os.path.join(DEMO_KEYS_DIR, keyname + '.pub'))
  // return rt.import_ed25519_privatekey_from_file(
      os.path.join(DEMO_KEYS_DIR, keyname), password='pw')
```

d. 将对应密钥存入[repo](#1. repo类)中

```
  repo.root.add_verification_key(key_root_pub)
  repo.timestamp.add_verification_key(key_timestamp_pub)
  repo.snapshot.add_verification_key(key_snapshot_pub)
  repo.targets.add_verification_key(key_targets_pub)
  repo.root.load_signing_key(key_root_pri)
  repo.timestamp.load_signing_key(key_timestamp_pri)
  repo.snapshot.load_signing_key(key_snapshot_pri)
  repo.targets.load_signing_key(key_targets_pri)
```

e.[添加一些起始image文件，主要用于 Web 前端](#3. add_target_to_imagerepo(target_fname, filepath_in_repo))

```
// API 
// 此目录下def add_target_to_imagerepo(target_fname, filepath_in_repo):
```

f.[write_to_live](#2. write_to_live())

g.[host](#4. host())

h.[listen](#5. listen())

### 2. write_to_live()

a. [将元数据文件写出到图像存储库的“metadata.staged”](#2. write(self, write_partial=False, consistent_snapshot=False, compression_algorithms=['gz']))

```
repo.mark_dirty(['timestamp', 'snapshot'])
repo.write() # will be writeall() in most recent TUF branch 
//tuf库tuf.repository_tool中write(self, write_partial=False, consistent_snapshot=False,compression_algorithms=['gz']):的调用
```

b. 将暂存元数据（从上面的写入操作）移动到实时元数据目录

``` if os.path.exists(os.path.join(demo.IMAGE_REPO_DIR, 'metadata')):
if os.path.exists(os.path.join(demo.IMAGE_REPO_DIR, 'metadata')):
  shutil.rmtree(os.path.join(demo.IMAGE_REPO_DIR, 'metadata'))

shutil.copytree(
    os.path.join(demo.IMAGE_REPO_DIR, 'metadata.staged'),
    os.path.join(demo.IMAGE_REPO_DIR, 'metadata'))
```

### 3. add_target_to_imagerepo(target_fname, filepath_in_repo)

a. 用途

用于攻击和更具体的演示。

给定指向目标目录中某个文件的文件名，添加该文件作为目标文件（计算其加密哈希和长度）

这不使用委派，而委派必须手动完成。

b. target_fname的内容校验

[tuf.formats.RELPATH_SCHEMA.check_match(target_fname)](#3. tuf.formats.RELPATH_SCHEMA.check_match(target_fname))

c. 将保存在filepath_in_repo的内容存储在target_fname中

```
repo_dir = repo._repository_directory
destination_filepath = os.path.join(repo_dir, 'targets', filepath_in_repo)

shutil.copy(target_fname, destination_filepath)  //destination_filepath需定义
```

d. [将文件路径（必须位于存储库的目标目录下）添加到目标对象](#4. add_target(self, filepath, custom=None))

### 4. host()

### 5. listen()

这专门用于演示网站前端。

侦听IMAGE_REPO_SERVICE_PORT对函数的 xml-rpc 调用：
    - add_target_to_image_repo
        - write_image_repo

### 6. mitm_arbitrary_package_attack(target_filepath)

模拟中间人任意包裹攻击，无需妥协密钥。 将恶意目标文件移动到映像存储库上，而无需更新元数据。

只使用了自带的一些os库，shutil库以及fobj库中的一些函数，可以直接使用

### 7. undo_mitm_arbitrary_package_attack(target_filepath)

撤消模拟的任意包攻击mitm_arbitrary_package_attack（）.将邪恶的目标文件移出，并将正常目标文件移回。

只使用了自带的一些os库，shutil库以及fobj库中的一些函数，可以直接使用

### 8. keyed_arbitrary_package_attack(target_filepath)

将新的恶意目标添加到映像存储库并签署恶意具有有效映像存储库时间戳、快照和目标的元数据钥匙。

a. 备份图像，然后在撤消函数中将其还原，而不是在撤消函数中将其更改的内容硬编码回。

这将要求我们选择一个临时文件位置。

```
 target_full_path = os.path.join(
      repo._repository_directory, 'targets', target_filepath) //调用了tuf库中repository_tool库中的类
```

[repo类](#1. repo类)

b. [将给定目标替换为恶意版本](#10. add_target_and_write_to_live(filename, file_content))

```
add_target_and_write_to_live(target_filepath, file_content='evil content')
```

### 9. undo_keyed_arbitrary_package_attack(target_filepath)

从keyed_arbitrary_package_attack中恢复。

1. 撤销现有时间戳、快照和目标键，并颁发新的键来替换它们。这将使用映像存储库的根密钥，这应该是一个离线密钥。
2. 将攻击者添加的恶意目标替换为干净的目标，就像攻击前一样。

a. [吊销可能已泄露的密钥，并用新密钥替换它们](#11. revoke_compromised_keys())

```
revoke_compromised_keys()
```

b. [将恶意目标替换为原始目标](#10. add_target_and_write_to_live(filename, file_content))

```
add_target_and_write_to_live(filename=target_filepath,
    file_content='Fresh firmware image')
```

### 10. add_target_and_write_to_live(filename, file_content)

创建目标的高级add_target_to_imagerepo（）文件，并将更改写入实时存储库。

```
with open(filename, 'w') as file_object:
  file_object.write(file_content)

filepath_in_repo = filename
add_target_to_imagerepo(filename, filepath_in_repo)
write_to_live()
```

### 11. revoke_compromised_keys()

撤销当前时间戳、快照和目标键，并添加新键对于每个角色。 这是通用函数的高级版本更新角色密钥。

a. 调用demo中_ init _.py

```
new_targets_keyname = 'new_maintargets'
new_timestamp_keyname = 'new_maintimestamp'
new_snapshot_keyname = 'new_mainsnapshot'

# Grab the old public keys.
old_targets_public_key = demo.import_public_key('maintargets')
old_timestamp_public_key = demo.import_public_key('maintimestamp')
old_snapshot_public_key = demo.import_public_key('mainsnapshot')
```

b. 取消旧公钥与角色的关联，对[tuf库的调用](#5. remove_verification_key(self, key))

```
repo.targets.remove_verification_key(old_targets_public_key)
repo.timestamp.remove_verification_key(old_timestamp_public_key)
repo.snapshot.remove_verification_key(old_snapshot_public_key)
```

c. 生成新的公钥和私钥并导入它们

d. 将新的公钥与角色关联，对[tuf库的调用](#6. add_verification_key(self, key, expires=None))

```
repo.targets.add_verification_key(new_targets_public_key)
repo.timestamp.add_verification_key(new_timestamp_public_key)
repo.snapshot.add_verification_key(new_snapshot_public_key)
```

e. TUF 分叉合并后，查看在重新分配顶级角色的签名密钥时，是否自动将 root 标记为日记。

```
repo.mark_dirty(['root'])
repo.targets.load_signing_key(new_targets_private_key)
repo.snapshot.load_signing_key(new_snapshot_private_key)
repo.timestamp.load_signing_key(new_timestamp_private_key)
```

对[tuf库的调用](#7. load_signing_key(self, key))

### 12. kill_server()

通过以下方式终止托管映像存储库的分叉进程Python的简单HTTP服务器。这不会影响存储库中的任何内容完全。host（） 可以在之后运行以再次开始托管。

```
global server_process
if server_process is None:
  print(LOG_PREFIX + 'No repository hosting process to stop.')
  return

else:
  print(LOG_PREFIX + 'Killing repository hosting process with pid: ' +
      str(server_process.pid))
  server_process.kill()
  server_process = None
```

## 二、director

### 1. clean_slate( use_new_keys=False,vin=_vin, ecu_serial=_ecu_serial):

a-d. 与image相同

e. 创建演示director实例

```
director_service_instance = director.Director(
    director_repos_dir=director_dir,
    key_root_pri=key_dirroot_pri,
    key_root_pub=key_dirroot_pub,
    key_timestamp_pri=key_dirtime_pri,
    key_timestamp_pub=key_dirtime_pub,
    key_snapshot_pri=key_dirsnap_pri,
    key_snapshot_pub=key_dirsnap_pub,
    key_targets_pri=key_dirtarg_pri,
    key_targets_pub=key_dirtarg_pub)   //对director类的一些成员的定义
```

```
director_service_instance.add_new_vehicle(vin)  //没有找到add_new_vehicle
```

f. 添加第一个目标文件，供Director开头的每辆车中的每个ECU使用。（目前 3）这会将文件从映像存储库复制到每个车辆存储库的目标目录中

```
for vin in inventory.ecus_by_vin:
  for ecu in inventory.ecus_by_vin[vin]:
    add_target_to_director(
        os.path.join(demo.IMAGE_REPO_TARGETS_DIR, 'infotainment_firmware.txt'),
        'infotainment_firmware.txt',
        vin,
        ecu)
```

### 2. write_to_live(vin_to_update=None)

与image中类似，只不过需根据不同vin选择性存入repo中

### 3. backup_repositories(vin=None)

备份上次写入的状态（“元数据.暂存”的内容目录）

```
repos_to_backup = director_service_instance.vehicle_repositories.keys() //没有找到这个在哪
```

```
repo_dir = director_service_instance.vehicle_repositories[
    vin]._repository_directory
```

其余用到的是python自带库，以及demo._ init_

tuf库[rt.load_repository( repo_dir)](#8. rt.load_repository( repo_dir))

### 4. restore_repositories(vin=None)

还原每个控制器存储库的上次备份。

### 5. revoke_compromised_keys()

撤销所有车辆的当前时间戳、快照和目标键，并为每个角色生成一个新密钥。 这是、用于更新角色键的通用函数。控制器服务实例也是
更新了关键更改。

和[image](#11. revoke_compromised_keys())中类似

### 6. sign_with_compromised_keys_attack(vin=None)

为所有车辆重新生成时间戳、快照和目标元数据，以及使用其以前吊销的密钥对其中每个角色进行签名。 默认键键的名称（导演、导演扣影、导演时间戳等）如果 prefix_of_previous_keys 为“无”，则使用文件，否则“prefix_of_previous_keys”被附加到它们前面。 这是一个高级别用于更新角色密钥的通用函数的版本。导演服务实例也会使用关键更改进行更新。

a. [备份](#3. backup_repositories(vin=None))

```
backup_repositories(vin)
```

b. 加载密钥

c. [删除密钥](#9. unload_signing_key(self, key))

d. [更新密钥](#2. write(self, write_partial=False, consistent_snapshot=False, compression_algorithms=['gz']))

### 7. undo_sign_with_compromised_keys_attack(vin=None)

撤消由 sign_with_compromised_keys_attack（） 执行的操作。 即将有效的元数据移动到活动目录和 metadata.staged 目录中，以及重新加载每个存储库的有效密钥。

a. 重新加载有效密钥，以便可以更新存储库对象以引用它们并替换已泄露的密钥集

```
valid_targets_private_key = demo.import_private_key('new_director')
valid_timestamp_private_key = demo.import_private_key('new_directortimestamp')
valid_snapshot_private_key = demo.import_private_key('new_directorsnapshot')

current_targets_private_key = director_service_instance.key_dirtarg_pri
current_timestamp_private_key = director_service_instance.key_dirtime_pri
current_snapshot_private_key = director_service_instance.key_dirsnap_pri
```

b. 在控制器服务中设置新的私钥。 这些密钥在所有车辆存储库之间共享

```
director_service_instance.key_dirtarg_pri = valid_targets_private_key
director_service_instance.key_dirtime_pri = valid_timestamp_private_key
director_service_instance.key_dirsnap_pri = valid_snapshot_private_key
```

[c. 恢复到控制器存储库中所有元数据的上次备份](#4. restore_repositories(vin=None))

```
restore_repositories(vin)
```

### 8. add_target_to_director(target_fname, filepath_in_repo, vin, ecu_serial)

用于攻击和更具体的演示。给定要添加的文件的文件名，相对于存储库的路径要将其复制到的根，车辆的VIN，其存储库应添加到 ECU 的串行目录中，添加该文件作为目标文件（计算其加密哈希和长度）到给定 VIN 的相应存储库。

和[image](#3. add_target_to_imagerepo(target_fname, filepath_in_repo))类似，只是具体存储的信息不同

### 9. host()

和[image](#4. host())类似

### 10. register_vehicle_manifest_wrapper(vin, primary_ecu_serial, signed_vehicle_manifest)

register_vehicle_manifest（）此包装器的目的是确保转到的数据director.register_vehicle_manifest是预期的。

```
if tuf.conf.METADATA_FORMAT == 'der':
  director_service_instance.register_vehicle_manifest(
      vin, primary_ecu_serial, signed_vehicle_manifest.data)
else:
  director_service_instance.register_vehicle_manifest(
      vin, primary_ecu_serial, signed_vehicle_manifest)
```

### 11. listen()

### 12. mitm_arbitrary_package_attack(vin, target_filepath)

模拟中间人任意包裹攻击，无需破坏任何密钥。 将恶意目标文件移动到控制器上的适当位置存储库，而不更新元数据。

和[image](#6. mitm_arbitrary_package_attack(target_filepath))中大部分相同，没用调用tuf库

### 13. undo_mitm_arbitrary_package_attack(target_filepath)

撤消模拟的任意包攻击mitm_arbitrary_package_attack（）.将恶性的目标文件移出，并将正常目标文件移回。

### 14. backup_timestamp(vin)

复制时间戳

```
timestamp_filename = 'timestamp.' + tuf.conf.METADATA_FORMAT
timestamp_path = os.path.join(demo.DIRECTOR_REPO_DIR, vin, 'metadata',
    timestamp_filename)
// tuf.conf.METADATA_FORMAT = 'json' # 'der'
backup_timestamp_path = os.path.join(demo.DIRECTOR_REPO_DIR, vin,
    'backup_' + timestamp_filename)

shutil.copyfile(timestamp_path, backup_timestamp_path)
```

### 15. replay_timestamp(vin)

将“backup_timestamp.der”移动到“timestamp.der”，有效地回滚指向以前版本的时间戳。 “backup_timestamp.der”必须已经存在在预期的路径上（可以通过backup_timestamp（vin）创建。在回滚 timestamp.der 之前，当前时间戳将保存到'current_timestamp.der'.

只是对文件的操作，没用到tuf库

### 16. restore_timestamp(vin)

回复时间戳

### 17. prepare_replay_attack_nokeys(vin)

为了通过 XMLRPC 暴露到 Web 前端，攻击脚本以准备执行重放攻击，不泄露对控制器的密钥。

对此目录下函数的调用

a. [backup_timestamp(vin=vin)](#14. backup_timestamp(vin))

b. [write_to_live(vin_to_update=vin)](#2. write_to_live(vin_to_update=None))

### 18. replay_attack_nokeys(vin)

实际执行重放攻击

 [replay_timestamp(vin=vin)](#15. replay_timestamp(vin))

### 19. undo_replay_attack_nokeys

撤消重放攻击，将车辆的控制器存储库放回正常状态

[restore_timestamp(vin)](#16. restore_timestamp(vin))

### 20. keyed_arbitrary_package_attack(vin, ecu_serial, target_filepath)

将新的恶意目标添加到车辆的控制器存储库中，将其分配给给定的ECU串行，并签署恶意元数据有效的控制器时间戳、快照和目标键。

a. 备份映像，然后在撤消功能中将其还原，而不是在撤消函数中对更改回的内容进行硬编码。这将要求我们选择一个临时文件位置。

```
target_full_path = os.path.join(
    director_service_instance.vehicle_repositories[vin]._repository_directory,
    'targets', target_filepath)
```

确保它存在于存储库中，否则中止此攻击，即编写为仅用于现有目标

```
if not os.path.exists(target_full_path):
  raise uptane.Error('Unable to attack: expected given image filename, ' +
      repr(target_filepath) + ', to exist, but it does not.')
```

b. 检查以确保给定文件也存在于存储库中。我们应该攻击存储库中已有的文件。考虑添加其他边缘情况检查（中断的内容，攻击）已经在进行中，等等。

```
add_target_and_write_to_live(
    target_filepath, file_content='evil content',
    vin=vin, ecu_serial=ecu_serial)
```

对本库下的[调用](#23.  add_target_and_write_to_live(filename, file_content, vin, ecu_serial))

### 21. undo_keyed_arbitrary_package_attack(vin, ecu_serial, target_filepath)

a. [吊销可能已泄露的密钥，并用新密钥替换它们](#5. revoke_compromised_keys())

```
revoke_compromised_keys()
```

b. [将恶意目标替换为原始目标](#23.  add_target_and_write_to_live(filename, file_content, vin, ecu_serial))

```
add_target_and_write_to_live(filename=target_filepath,
    file_content='Fresh firmware image', vin=vin, ecu_serial=ecu_serial)
```

### 22. clear_vehicle_targets(vin)

从当前控制器中删除对给定车辆的所有说明元数据。

这不会执行write_to_live。更改完成后，您应该调用它来写入新的元数据。

可以调用它来清除ECU的现有指令，以便可以向该ECU提供不同固件的指令。

```
director_service_instance.vehicle_repositories[vin].targets.clear_targets() //没找到啊
```

### 23.  add_target_and_write_to_live(filename, file_content, vin, ecu_serial)

```
with open(filename, 'w') as file_object:
  file_object.write(file_content)

# The path that will identify the file in the repository.
filepath_in_repo = filename

add_target_to_director(filename, filepath_in_repo, vin, ecu_serial)
write_to_live(vin_to_update=vin)
```

也调用本目录下的函数

[add_target_to_director(filename, filepath_in_repo, vin, ecu_serial)](#8. add_target_to_director(target_fname, filepath_in_repo, vin, ecu_serial))

[write_to_live(vin_to_update=vin)](#2. write_to_live(vin_to_update=None))

### 24. kill_server()

与[image](#12. kill_server())库相同

## 三、primary

## 四、secondary

### 函数接口一

```
secondary:clean_slate  初始化函数（76-180）

```

### 函数接口二

```
secondary:create_secondary_pinning_file()  加载固定模板，设置客户端目录（186-215）
return fname_to_create  返回设置文件名
```

### 函数接口三

```
submit_ecu_manifest_to_primary(signed_ecu_manifest=None)  提交manifest（221-261）
signed_ecu_manifest
most_recent_signed_ecu_manifest 两个变量来判断签名进度
```

### 函数接口四

```
secondary:update_cycle()  周期验证升级（考虑errors情况较多）279-520
  global secondary_ecu
  global current_firmware_fileinfo
  global attacks_detected   全局可使用变量
  # TODO: Determine if something should be added to attacks_detected here.
```

### 函数接口五

```
secondary：generate_signed_ecu_manifest()  （526-537）
most_recent_signed_ecu_manifest = secondary_ecu.generate_signed_ecu_manifest(
      attacks_detected)
```

### 函数接口六

```
secondary:ATTACK_send_corrupt_manifest_to_primary() 在不更新签名的情况下修改 ECU 清单(543-568)
submit_ecu_manifest_to_primary(corrupt_signed_manifest)
```

### 函数接口七

```
register_self_with_director():（574-591）
```

### 函数接口八

```
register_self_with_primary()  （597-609）
 server.register_new_secondary(secondary_ecu.ecu_serial)
```

### 函数接口九

```
enforce_jail(fname, expected_containing_dir)  确认是预期的目录（615-628）
abs_fname = os.path.abspath(os.path.join(expected_containing_dir, fname))
return abs_fname
```

### 函数接口十

```
clean_up_temp_file(filename)  清理临时文件 （634-639）
```

### 函数接口十一 

```
looping_update() 执行函数，反复更新 （663-670）
```

## 五、timeserver

充当符合 Uptane 的时间服务器：
   - 通过 XML-RPC 侦听来自车辆的请求。
   - 接收随机数列表并以签名时间证明作为响应列出了这些随机数。

主要还是通过listen监听端口获取命令

主要看listen（）里的相应执行函数就行了

### get_time(nonces):

time格式为
time_attestation = {
    'time': clock,
    'nonces': nonces
  }


### get_signed_time_der(nonces):

与 get_signed_time 相同，但将生成的 Python 字典转换为 ASN.1 表示，将其编码为 DER（可分辨编码规则），将签名替换为数据“签名”部分的 DER 编码散列上的签名（ 时间和随机数）。

uptane.formats

uptane.common

使用这些库进行签名和格式转化

## 六、tuf

### 1. repo类

a. 密钥添加

```
repo.rolename.load_signing_key(keyname)  //向角色添加“密钥”。 添加一个键，该键应仅包含公共部分，表示相应的私钥和签名											   该角色有望提供。 需要签名阈值以将角色视为已正确签名。 如果元数据文件包含签名阈											  值不足，则不得接受。

repo.rolename.load_signing_key(keyname)  //加载角色密钥，其中必须包含专用部分，以便该角色当角色的元数据文件最终写入磁盘。

```

b. 一些定义

```
repository_directory: 包含元数据和目标的存储库的根文件夹子目录。
metadata_directory: 元数据子目录包含顶级的文件角色，包括从“targets.json”委派的所有角色。
targets_directory: 目标子目录包含所有目标文件，这些文件由客户端下载并在 TUF 元数据中引用。 哈希和文件大小列在元数据文件中，以					  便它们安全下载。 元数据文件在顶级中类似地被引用元数据。
repository_name: (optional; default: 'default')：这是将在内部用于引用存储库的名称。当同时使用多个存储库时，这一点很重要。
     											 roledb 全局角色中的条目将区分角色和不同角色使用此名称的存储库。
```

### 2. write(self, write_partial=False, consistent_snapshot=False, compression_algorithms=['gz'])

将所有 JSON 元数据对象写入其相应的文件。
write（） 在要写入的任何角色元数据时引发异常磁盘无效，例如签名阈值不足，丢失私钥等

### 3. tuf.formats.RELPATH_SCHEMA.check_match(target_fname)

### 4. add_target(self, filepath, custom=None)

将文件路径（必须位于存储库的目标目录下）添加到目标对象

### 	 add_targets(self, list_of_targets)

添加目标文件路径的列表（全部相对于“self.targets_directory”）此方法实际上不会在文件系统上创建文件，这目标列表必须已存在。

### 5. remove_verification_key(self, key)

从角色当前识别的角色密钥列表中删除“密钥”，该角色需要一个阈值数量的签名。

### 6. add_verification_key(self, key, expires=None)

### 7. load_signing_key(self, key)

加载角色密钥，其中必须包含专用部分，以便该角色 当角色的元数据文件最终写入磁盘。

### 8. rt.load_repository( repo_dir)

返回包含已加载元数据文件内容的存储库对象从存储库中。

### 9. unload_signing_key(self, key)

删除以前加载的角色私钥（即load_signing_key（））。“密钥”的密钥 ID 将从已识别签名列表中删除钥匙。
