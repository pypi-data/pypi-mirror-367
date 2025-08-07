# Gaokao MCP Server
这是一个 Model Context Protocol Server，使大语言模型能够获取关于中国高考的相关信息，从而为考生的志愿填报提供有力的帮助

## 可用工具
- `query_major_info` - 查询某个专业的信息
    - `major_name` (字符串，必需): 专业名称
    - `major_level` (字符串，必需): 专业层次

- ......

## 安装
### 使用 uv (推荐)
当使用 [`uv`](https://docs.astral.sh/uv/) 时，无需特定安装。我们将使用 [`uvx`](https://docs.astral.sh/uv/guides/tools/) 直接运行mcp-server-gaokao。

```bash
uvx mcp-server-gaokao
```

JSON Configuration:
```json
{
  "mcpServers": {
    "gaokao": {
      "type": "stdio",
      "command": "uvx",
      "args": ["mcp-server-gaokao"]
    }
  }
}

```
### 使用 PIP
或者，你可以通过 pip 安装 `mcp-server-gaokao`：

```bash
pip install mcp-server-gaokao
```

安装后，你可以作为脚本运行：

```bash
python -m mcp_server_gaokao
```

JSON Configuration:
```json
{
  "mcpServers": {
    "gaokao": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "mcp-server-gaokao"]
    }
  }
}
```

## Server 运行参数
### 返回格式
工具运行结果的返回格式支持 JSON 和 Markdown。默认情况下，Server 返回 JSON 格式的数据。你可以通过设置 `--return_format` 参数来指定返回 Markdown 格式：
```bash
# 使用uv
uvx mcp-server-gaokao --return_format markdown
# 使用pip
python -m mcp_server_gaokao --return_format markdown
```

## 使用示例
### query_major_info
```
User：请查一下计算机科学与技术专业的详细信息
```
大语言模型选择该工具，该工具执行完成后返回专业信息：
- 基本信息（类别、代码、男女比例、修业年限等）
- 就业情况（就业率、薪酬水平、行业分布等）

**注意事项:**
- 请使用标准的专业名称，避免使用简称
- 如果简称对应多个专业（如"自动化"），大语言模型或许会要求你确认具体专业
- 支持本科和专科两个层次的专业查询，不指定的情况下，大语言模型大概率会针对本科层次进行查询

## 调试
你可以使用[`MCP Inspector`](https://github.com/modelcontextprotocol/inspector)来调试此Server。对于 uvx 安装：

```bash
npx @modelcontextprotocol/inspector uvx mcp-server-gaokao
```

或者如果你在特定目录中安装了包或正在开发它：

```bash
cd path/to/mcp-server-gaokao
npx @modelcontextprotocol/inspector uv run mcp-server-gaokao
```

## 数据来源
本项目的专业信息来源于网络公共数据，仅供学习和研究使用。

## License
mcp-server-gaokao 采用 MIT 许可证。这意味着你可以自由使用、修改和分发该软件，但需遵守 MIT 许可证的条款和条件。有关更多详细信息，请参见项目存储库中的 LICENSE 文件。