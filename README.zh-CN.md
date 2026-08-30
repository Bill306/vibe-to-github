# vibe-to-github

[English](README.md) | **简体中文**

`vibe-to-github` 是一个 Codex Skill，用于把本地 vibe coded 项目整理成别人能够看懂、运行并信任的 GitHub 仓库。

## 要解决的问题

很多 vibe coded 项目虽然能在作者自己的电脑上运行，但发布到 GitHub 时可能存在 README 与实际功能不一致、安装步骤不清楚、意外包含凭据或隐私数据、暴露本地路径、提交生成文件，或者没有认真选择许可证等问题。这个 Skill 将这些检查纳入发布流程，并明确区分本地整理权限和远程发布权限。

## 主要功能

- **三种工作模式** — 只读检查、仅在本地整理，以及获得明确远程操作确认后的正式发布。
- **README 内容契约** — 必须说明项目解决的问题、主要功能、安装方法、使用方法和真实的输入输出示例。
- **自适应排版** — 根据项目选择 App/Product、Library/CLI 或 Community/Content 模板，而不是给所有项目硬套同一种结构。
- **许可证决策门槛** — 解释常见软件和内容许可证，检查第三方素材边界，并要求用户确认最终选择。
- **只读发布前检查** — 检查疑似密钥、隐私数据、本地路径、生成文件、大文件、Git 历史风险和远端凭据，不输出匹配到的敏感值。
- **发布确认清单** — 在任何远程修改前展示仓库可见性、目标地址、改动文件、许可证、安全检查覆盖范围和验证证据。
- **受限的 Git 行为** — 禁止强制推送、擅自重写历史、替换远端、附带部署，以及在脏工作区中进行大范围暂存。

## 安装

将此文件夹复制到兼容的 Codex Skills 目录：

```bash
cp -R vibe-to-github ~/.codex/skills/vibe-to-github
```

Skill 自带的 Python 检查脚本只使用标准库。仓库和历史检查需要 Git。单独安装的 `gitleaks` 可以增加 Git 历史内容级扫描；Skill 不会自动安装它。

## 使用方法

调用时提供本地项目路径和需要的工作模式：

```text
使用 $vibe-to-github 只读检查 /path/to/my-project，不要修改文件。
```

```text
使用 $vibe-to-github 把 /path/to/my-project 整理成 GitHub-ready，但暂时不要发布。
```

```text
使用 $vibe-to-github 整理这个项目，并在创建私有 GitHub 仓库前先向我展示发布确认清单。
```

也可以直接运行确定性检查脚本：

```bash
python3 scripts/preflight.py /path/to/my-project --history
python3 scripts/validate_readme.py /path/to/my-project
```

## 输入与输出示例

**输入**

```text
帮我把这个 Next.js 原型整理成 GitHub-ready，暂时不要发布。
```

**输出**

```text
状态：BLOCKED
README：缺少输入输出示例
安全检查：发现可能包含凭据的 .env.local
历史检查覆盖：仅检查历史敏感文件名；gitleaks 不可用
远程操作：未执行
下一步：轮换任何可能已经暴露的真实凭据，创建经过脱敏的 .env.example，
并在用户批准本地修改后重新运行检查。
```

Skill 只报告文件名和问题类型，不输出密钥值。

## 仓库结构

```text
.
├── README.md
├── README.zh-CN.md
├── SKILL.md
├── agents/openai.yaml
├── assets/templates/
├── examples/
├── references/
├── scripts/
├── AGENTS.md
└── LICENSE
```

## 已知限制

- 启发式密钥和隐私检查可能产生误报或漏报。
- 完整的 Git 历史内容级扫描需要兼容的外部工具，例如 `gitleaks`。
- README 校验器可以检查文档结构和部分命令一致性，但不能证明文字描述与业务行为完全一致。
- 许可证说明只用于教育参考，不构成法律建议。
- Build 或 Push 成功不代表项目已具备生产正确性或安全性。

## 安全与隐私

对于目标项目，自带脚本仅执行只读检查。它们不会删除文件、重写 Git 历史、上传数据、安装依赖或创建 GitHub 仓库。检查结果会脱敏，只显示文件名、问题类别和大致行号。

如果怀疑真实凭据已经泄露，应先轮换或撤销凭据，再处理仓库历史。详见 [references/security-checklist.md](references/security-checklist.md)。

## 参与贡献

请保持检查规则保守、输出内容脱敏，并明确保留每个授权门槛。提交改动前运行仓库验证：

```bash
scripts/validate.sh
```

## 许可证

MIT License，详见 [LICENSE](LICENSE)。
