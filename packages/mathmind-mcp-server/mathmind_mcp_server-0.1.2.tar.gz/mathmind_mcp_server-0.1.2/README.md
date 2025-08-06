# MCP 文档

# 部署

目录：/opt/mathmind-mcp-server

部署命令：

```jsx
git pull
docker rm -f mathmind-mcp-server
docker build -t mathmind-mcp-server .
docker run -d --name mathmind-mcp-server --restart=always -p 8000:8000 mathmind-mcp-server
```

后边可以改成自动化部署，比如通过 github-action

# 域名

https://mcp.mathmind.cn

nginx 配置：/etc/nginx/conf.d/mcp.mathmind.cn.conf


# Run
```shell
docker build -t mathmind-mcp-server .
docker rm -f mathmind-mcp-server
docker run -d \
  --name mathmind-mcp-server \
  --restart=always \
  -p 8000:8000 mathmind-mcp-server
```