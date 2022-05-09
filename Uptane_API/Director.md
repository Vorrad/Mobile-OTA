# Director

呈现给primary的 XMLRPC 接口：
     register_ecu_serial(ecu_serial, ecu_public_key, vin,is_primary=False)
     submit_vehicle_manifest（vin，ecu_serial，signed_ecu_manifest）

   呈现给网站的 XMLRPC 接口：
     add_new_vehicle(vin)
     add_target_to_director(target_filepath, filepath_in_repo, vin, ecu_serial) <--- 分配给车辆
     write_director_repo() <--- 将阶段移动到实时/将新添加的目标添加到实时存储库
     get_last_vehicle_manifest(vin)
     get_last_ecu_manifest(ecu_serial)
     register_ecu_serial(ecu_serial, ecu_key, vin, is_primary=False)

这些接口具体实现都可以到listen（）中去找相应命令



## clean_slate() 初始化流程与image类似

创建./director文件夹

产生、引入密钥

> generate_key
>
> import_public_key
>
> import_private_key

创建Director实体库

> API是uptane**.**services**.**director中的Direcor类

添加车辆信息

> add_new_vehicle

添加第一个目标文件，供每辆车中的每个 ECU 使用
Director开始了。 （目前 3 个）
这会将文件从image存储库复制到每个车辆存储库的目标目录。

> **for** vin **in** inventory**.**ecus_by_vin:
>
>   **for** ecu **in** inventory**.**ecus_by_vin[vin]:
>
> 从uptane**.**services**.**inventorydb中导入的全局变量表示每辆车的每个ecu
>
> 
>
> add_target_to_director
>
> 给定要添加的文件的文件名、相对于要复制到的存储库根目录的路径、应将其添加到其存储库的车辆的 VIN 以及 ECU 的串行目录，将该文件添加为目标文件（计算 其加密哈希和长度）到给定 VIN 的适当存储库。
>
>    <参数>
>      target_fname
>        要作为目标添加到 Director's 的文件的完整文件名
>        目标角色元数据。 该文件不必是任何特定的
>        地方; 它将被复制到存储库目录结构中。
>
>  filepath_in_repo
>    相对于存储库目标目录根目录的路径
>    客户端将保存和访问此文件的位置。 （例如'file1.txt'或“刹车/固件.tar.gz”）
>
>  ecu_serial
>    在目标元数据中分配此目标的 ECU。
>    符合 uptane.formats.ECU_SERIAL_SCHEMA

签署和托管初始存储库元数据(与image一样，函数名也一样)

 **write_to_live**()

对每辆车

将元数据文件写入车辆库的“metadata.staged”

将暂存的元数据（从上面的写入）移动到实时元数据目录。

 **host**()

将 Director 存储库（http 服务元数据文件）作为单独的进程托管。 应该用 kill_server() 停止。

还必须运行 listen() 来启动 Director 服务（在 xmlrpc 上运行）。

如果这个模块已经启动了一个服务器进程来托管 repo，那么什么都不会做。

 **listen**() 

在 DIRECTOR_SERVER_PORT 上侦听 xml-rpc 对函数的调用：
   - submit_vehicle_manifest
   -  register_ecu_serial

与primary通过http服务器传递数据（大概



## 其他一些函数

**backup_repositories**(vin=**None**):

备份上次写入的状态（每个存储库中“metadata.staged”目录的内容）。

 元数据从“{repo_dir}/metadata.staged”复制到 '{repo_dir}/metadata.backup'

 **restore_repositories**(vin=**None**)

恢复每个 Director 存储库的上次备份。

 元数据从“{repo_dir}/metadata.backup”复制到 '{repo_dir}/metadata.staged' 和 '{repo_dir}/metadata'

**revoke_compromised_keys（）**

撤销所有车辆的当前时间戳、快照和目标密钥，并为每个角色生成一个新密钥。 这是更新角色键的通用函数的高级版本。 Director服务实例也随着关键变化而更新。

**sign_with_compromised_keys_attack**(vin=**None**)

为所有车辆重新生成时间戳、快照和目标元数据，并使用之前撤销的密钥对每个角色进行签名。 如果 prefix_of_previous_keys 为 None，则使用密钥文件的默认密钥名称（director、directorsnapshot、directortimestamp 等），否则在它们前面加上“prefix_of_previous_keys”。 这是更新角色键的通用功能的高级版本。 导演服务实例也随着关键变化而更新。

**undo_sign_with_compromised_keys_attack**(vin=**None**):

撤消由 sign_with_compromised_keys_attack() 执行的操作。 即，将有效元数据移动到 live 和 metadata.staged 目录，并为每个存储库重新加载有效密钥。

**register_vehicle_manifest_wrapper**

此函数是director.Director::register_vehicle_manifest() 的包装器。

   这个包装器的目的是确保进入 director.register_vehicle_manifest 的数据是预期的。

   在demo中，有两种场景：

 - 如果我们使用 ASN.1/DER，那么车辆清单是一个二进制对象，并且 signed_vehicle_manifest 必须包装在一个 XMLRPC Binary() 对象中。 参考实现没有 XMLRPC 的概念（也不应该），因此必须从 XMLRPC Binary() 对象中提取车辆清单，在这种情况下，该对象是 signed_vehicle_manifest。

 - 如果我们使用任何其他数据格式/编码（例如 JSON），则车辆清单作为参考实现已经可以理解的对象传输，我们只需将参数传递给导向器模块。
