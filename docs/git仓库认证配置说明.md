# Git仓库认证配置说明

## 仓库信息
- 仓库地址: https://github.com/18673820416-core/RAG-ststem.git
- 用户名: 18673820416-core

## 认证配置方法

### 方法1：使用Personal Access Token（推荐）
1. 访问GitHub设置页面
2. 进入Developer settings > Personal Access Tokens
3. 生成新的Token，赋予repo权限
4. 使用Token代替密码进行认证

### 方法2：使用Git Credential Manager
1. Git会自动提示保存凭据
2. 凭据将安全存储在系统凭据管理器中

## 仓库状态
- 本地仓库已配置忽略所有数据文件
- 只推送源代码和配置文件
- 远程仓库地址已保存在本地配置中

## 使用说明
下次推送时，只需运行：
```
git push origin main
```
系统会提示您输入认证信息，输入Token或密码后，凭据将被缓存。