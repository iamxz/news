# 代理配置指南

## 为什么需要代理？

访问国际新闻网站（如 Reuters、BBC、NYT 等）时，可能会遇到网络限制。配置代理可以解决这个问题。

## 快速配置

### 1. 编辑 .env 文件

```bash
# 打开 .env 文件
nano .env

# 或使用其他编辑器
vim .env
```

### 2. 添加代理配置

```bash
# HTTP 代理
HTTP_PROXY=http://127.0.0.1:7890

# HTTPS 代理（推荐与 HTTP 保持一致）
HTTPS_PROXY=http://127.0.0.1:7890
```

### 3. 测试代理

```bash
python main.py test-proxy
```

如果看到 "✅ 代理测试成功！"，说明配置正确。

## 代理格式说明

### HTTP 代理
```bash
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

### HTTPS 代理
```bash
HTTP_PROXY=https://127.0.0.1:7890
HTTPS_PROXY=https://127.0.0.1:7890
```

### SOCKS5 代理
```bash
HTTP_PROXY=socks5://127.0.0.1:1080
HTTPS_PROXY=socks5://127.0.0.1:1080
```

### 带认证的代理
```bash
HTTP_PROXY=http://username:password@127.0.0.1:7890
HTTPS_PROXY=http://username:password@127.0.0.1:7890
```

## 常见代理软件

### Clash
- 默认端口：7890
- 配置示例：
  ```bash
  HTTP_PROXY=http://127.0.0.1:7890
  HTTPS_PROXY=http://127.0.0.1:7890
  ```

### V2Ray
- 默认端口：1080（SOCKS5）或 10809（HTTP）
- 配置示例：
  ```bash
  HTTP_PROXY=http://127.0.0.1:10809
  HTTPS_PROXY=http://127.0.0.1:10809
  ```
  或
  ```bash
  HTTP_PROXY=socks5://127.0.0.1:1080
  HTTPS_PROXY=socks5://127.0.0.1:1080
  ```

### Shadowsocks
- 默认端口：1080
- 配置示例：
  ```bash
  HTTP_PROXY=socks5://127.0.0.1:1080
  HTTPS_PROXY=socks5://127.0.0.1:1080
  ```

## 测试代理

### 测试默认 URL（Google）
```bash
python main.py test-proxy
```

### 测试特定新闻网站
```bash
# 测试 BBC
python main.py test-proxy -u https://www.bbc.com

# 测试 Reuters
python main.py test-proxy -u https://www.reuters.com

# 测试 NYT
python main.py test-proxy -u https://www.nytimes.com
```

## 故障排查

### 问题 1：代理测试失败

**可能原因**：
1. 代理软件未运行
2. 端口号错误
3. 代理地址错误

**解决方法**：
```bash
# 1. 检查代理软件是否运行
# 2. 确认端口号（通常在代理软件设置中查看）
# 3. 尝试不同的代理协议（HTTP/SOCKS5）
```

### 问题 2：抓取新闻时超时

**可能原因**：
1. 代理速度慢
2. 代理不稳定

**解决方法**：
```bash
# 1. 更换代理节点
# 2. 检查代理软件的连接状态
# 3. 尝试直连（临时移除代理配置）
```

### 问题 3：部分网站无法访问

**可能原因**：
1. 代理不支持该网站
2. 网站屏蔽了代理 IP

**解决方法**：
```bash
# 1. 更换代理节点
# 2. 使用不同的代理协议
```

## 不使用代理

如果你的网络环境可以直接访问国际网站，可以不配置代理：

```bash
# 在 .env 文件中保持为空或注释掉
# HTTP_PROXY=
# HTTPS_PROXY=
```

## 安全提示

1. **不要在公共场合分享你的 .env 文件**（包含代理配置）
2. **使用可信的代理服务**
3. **定期更换代理密码**（如果使用带认证的代理）
4. **不要将 .env 文件提交到 Git**（已在 .gitignore 中）

## 验证配置

配置完成后，运行完整测试：

```bash
# 1. 测试代理
python main.py test-proxy

# 2. 测试抓取（抓取少量新闻验证）
python main.py fetch -s reuters

# 3. 查看结果
python main.py show -l 5
```

如果能成功抓取新闻，说明代理配置正确！

## 高级配置

### 为不同协议使用不同代理

```bash
# HTTP 使用一个代理
HTTP_PROXY=http://127.0.0.1:7890

# HTTPS 使用另一个代理
HTTPS_PROXY=http://127.0.0.1:7891
```

### 代理自动切换

目前不支持自动切换，如需更换代理：

1. 修改 .env 文件中的代理配置
2. 重启应用或守护进程

## 性能优化

### 选择合适的代理节点

- 优先选择地理位置近的节点
- 选择负载低的节点
- 避免使用免费公共代理（不稳定且不安全）

### 代理池（未来功能）

计划在未来版本中支持：
- 多代理配置
- 自动切换
- 负载均衡

## 常见问题

**Q: 必须配置代理吗？**  
A: 不是必须的。如果你的网络可以直接访问国际网站，不需要配置代理。

**Q: 支持哪些代理协议？**  
A: 支持 HTTP、HTTPS、SOCKS5。

**Q: 可以使用免费代理吗？**  
A: 技术上可以，但不推荐。免费代理通常不稳定且有安全风险。

**Q: 代理配置后需要重启吗？**  
A: 是的，修改 .env 后需要重启应用或守护进程。

**Q: 如何知道代理是否在工作？**  
A: 运行 `python main.py test-proxy` 测试。

## 获取帮助

如果遇到问题：

1. 查看日志：应用会输出详细的错误信息
2. 测试代理：`python main.py test-proxy`
3. 检查代理软件：确保代理软件正常运行
4. 提交 Issue：在 GitHub 上提交问题

---

**配置完成后，就可以开始使用了！**

```bash
# 启动守护进程
./daemon.sh

# 或手动抓取
python main.py fetch
```
