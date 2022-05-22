## secondary

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