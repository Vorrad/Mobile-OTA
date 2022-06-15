# image

## **clean_slate**

创建*./imagerepo/targets*，创建file.txt、infotainment_fireware.txt（不知道干嘛的）

在./repomain下创建image库

> API：**tuf**.**repository_tool.create_new_repository**

产生相关密钥（这里照着源码用应该就行）

> **generate_key**-------**generate_and_write_ed25519_keypair**
>
> **import_public_key** ------ **import_ed25519_publickey_from_file**
>
> **import_private_key**-------**import_ed25519_privatekey_from_file**
>
> **add_verification_key**  这个应该直接在tuf中定义
>
> 前三个都在demo的_ init _.py中定义，实质调用的还是**tuf.repository_tool**中的API

添加一些起始image文件，主要用于 Web 前端。执行下图中的过程。

![image-20220508214801680](C:\Users\user\AppData\Roaming\Typora\typora-user-images\image-20220508214801680.png)

> add_target_to_imagerepo
>
> 在本文件下定义
>
> 用于攻击和更具体的演示。
>
> 给定一个指向目标目录中文件的文件名，将该文件添加为目标文件（计算其加密哈希和长度）
>
> <参数>
> target_fname
> 要作为目标添加到图像的文件的完整文件名存储库的目标角色元数据。 该文件将被复制到给定路径中存储库的目标目录。
>
> filepath_in_repo
> 这是用于标识存储库中文件的名称，并且相对于存储库根目录的文件路径目标目录。
>
> 

 签署和托管初始存储库元数据

**write_to_live**

将元数据文件写入图像存储库的“metadata.staged”

将暂存的元数据（从上面的写入）移动到实时元数据目录。

**host**()  **listen**() 实现下面这两步

![image-20220508215926381](C:\Users\user\AppData\Roaming\Typora\typora-user-images\image-20220508215926381.png)

**listen()**

在 IMAGE_REPO_SERVICE_PORT 上侦听 xml-rpc 对函数的调用

listen里实现了两个demo网站的接口

演示网站上呈现的 XMLRPC 接口，这两个接口函数分别是add_target_to _imagerepo和wwrite_to_live：
     add_target_to_image_repo(target_filepath, filepath_in_repo) <--- 添加到暂存映像存储库
     write_image_repo() <--- 将阶段移动到实时/将新添加的目标添加到实时存储库

> 这里我没搞太懂，大概就是通过xml-rpc可以执行这两个功能

剩下函数都是关于攻击，恢复，暂时应该不需要