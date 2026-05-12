## IndieTracks 团队新手上路指南

欢迎加入！克隆仓库后，跟着这份指南，你就能在本地把整个项目跑起来。  
**适用系统**：Windows（macOS/Linux 用户请参考括号内的说明）

---

### 📦 第一步：你需要提前安装的软件

安转选项看不懂的去搜怎么安装，跟着流程走

| 软件              | 用途           | 安装说明                                                                                                                                                           |
| :-------------- | :----------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Node.js 22+** | 前端运行时        | [官网下载](https://nodejs.org)，选 LTS 版本，安装时勾选“自动添加 PATH”**之前装过的查看版本号，太老的升级**                                                                                       |
| **JDK 25**      | 后端运行         | [下载 JDK 25](https://jdk.java.net/25)，解压并配置 `JAVA_HOME` 环境变量<br>**可以在IDEA里面下载**                                                                                 |
| **PostgreSQL**  | 数据库          | [官网下载](https://www.postgresql.org/download/windows)，安装时记住设置的超级用户密码（如 `postgres`）**最高版本**                                                                       |
| **MinIO**       | 对象存储（存音频/图片） | [MinIO对象存储 Windows — MinIO中文文档 \| MinIO Windows中文文档](https://www.minio.org.cn/docs/minio/windows/index.html)，解压后将 `minio.exe` 放入项目 `tools/` 目录，**稍后可以写给脚本给你们** |
| **Git**         | 版本管理         | [官网下载](https://git-scm.com/download/win)，默认安装即可                                                                                                                |
| **Sourcetree**  | Git图形化管理工具   | [安装Sourcetree \|Sourcetree \|阿特拉西安文献](https://confluence.atlassian.com/get-started-with-sourcetree/install-sourcetree-847359094.html) **强推，如果不想学命令行的话**        |
|                 |              |                                                                                                                                                                |

> **验证安装**：打开 **命令提示符**（或 PowerShell），输入以下命令，有版本号输出就表示成功。
> ```bash
> node -v
> java -version
> git --version
> ```

---

### 📥 第二步：克隆仓库并安装项目依赖

1.  在你喜欢的文件夹中，右键选择 **“Git Bash Here”**（或打开终端切到目标目录），执行：
    ```bash
    git clone https://github.com/lixKRT/IndieTracks.git
    cd indietracks
    ```

2.  **安装前端依赖**：
    ```bash
    cd frontend
    npm install
    cd ..
    ```

3.  **安装后端依赖**：
    首先确认 `backend` 目录里已有 `pom.xml`，然后执行：
    ```bash
    cd backend
    # Windows 用 mvnw.cmd
    mvnw.cmd clean install -DskipTests
    # Linux/Mac 用 ./mvnw clean install -DskipTests
    cd ..
    ```
    > 如果提示 `mvnw` 不是命令，可能是权限问题，可以尝试 `.\mvnw.cmd` (Windows) 或 `chmod +x mvnw && ./mvnw` (Linux/Mac)。

---

### 🗄️ 第三步：初始化数据库

1.  **启动 PostgreSQL 服务**（通常安装后会自动启动，如果没启动可以到“服务”里找到 `postgresql-x64-16` 并手动启动）。
2.  **创建数据库**：打开 **DBeaver** 或 **pgAdmin**（数据库管理软件，vscode插件，IDEA自带的都可以），连接到本地 PostgreSQL（默认端口 `5432`，用户 `postgres`，密码是你安装时设置的），新建一个数据库，起名为 `indietracks`。
3.  **导入表结构**：在 DBeaver 中打开 `indietracks` 数据库，执行项目根目录下的 `database/init.sql` 文件（全选内容后运行）。这样所有表就建好了。
4.  （可选）如果你手头有种子数据，同样方式导入 `database/seed.sql`，让页面有初始内容。

---

### 🧩 第四步：配置后端数据库连接

打开 `backend/src/main/resources/application.yml`，找到数据库配置部分，修改成你的本地信息：

```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/indietracks
    username: postgres           # 你的数据库用户名
    password: 你的密码           # 你的数据库密码
  jpa:
    hibernate:
      ddl-auto: none             # 因为我们已经用 init.sql 建好表，这里选 none 不自动改表
    show-sql: true               # 开发时打印 SQL，方便调试
```

> ⚠️ **注意**：这个文件里不要包含真实密码！如果你本地测试用，没关系；但后续提交代码时务必把这个文件加进 `.gitignore`（或者使用环境变量）。目前团队协作可以暂时保留本地修改。

---

### 🚀 第五步：启动项目

#### 🔹 如果你只想开发前端页面（不连后端）

在 `frontend` 目录下，项目已经内置了模拟数据 `src/api/mock.js`，你可以直接启动前端开发服务器：

```bash
cd frontend
npm run dev
```
浏览器访问 `http://localhost:5173`，就能看到首页、专辑详情（模拟数据）。  
此时**不需要启动后端和 MinIO**。

#### 🔹 如果你需要跑全栈（前后端 + 数据库 + MinIO）

按以下顺序启动：

1.  **启动 MinIO**（在项目根目录）：
    ```bash
    # Windows 命令，在项目根目录打开终端
    tools\minio.exe server data\minio-data --console-address ":9001" --address ":9000" --memory 128MB
    ```
    看到 `API: http://127.0.0.1:9000` 和 `WebUI: http://127.0.0.1:9001` 表示启动成功。  
    （默认 Access Key: `minioadmin`，Secret Key: `minioadmin`）

2.  **启动后端 Spring Boot**（新开一个终端）：
    ```bash
    cd backend
    mvnw.cmd spring-boot:run
    ```
    当看到 `Undertow started on port(s) 8080` 时，后端就绪。

3.  **启动前端**（再开一个终端）：
    ```bash
    cd frontend
    npm run dev
    ```
    浏览器打开 `http://localhost:5173`，前端默认请求 `/api` 会自动代理到后端的 8080 端口（Vite 已配置好代理，无需额外设置）。

#### 🔹 如果你还需要运行爬虫

在项目根目录，确保 Python 虚拟环境已创建（见项目创建脚本），然后：
```bash
cd crawler
env\Scripts\activate          # Windows
pip install -r requirements.txt
scrapy crawl dizzylab_spider #TODO 这个后面应该会改
```
爬虫会把数据写入你本地 PostgreSQL 的 `indietracks` 数据库，并将音频/图片上传到 MinIO。

---

### ❓ 常见问题

**Q：启动前端时报错 “Cannot find module ...”**  
A：请确保在 `frontend` 目录下执行过 `npm install`，如果仍有问题，删除 `node_modules` 文件夹后重新 `npm install`。

**Q：后端启动失败，提示数据库连接错误**  
A：检查 PostgreSQL 服务是否启动，`application.yml` 里的用户名密码是否正确，数据库 `indietracks` 是否已创建。

**Q：MinIO 打不开控制台**  
A：请确认 `tools/minio.exe` 是否存在，并已按命令启动。如果端口冲突（9000 或 9001 被占用），可以换端口。

**Q：我想直接在 Windows 上用 Nginx 反向代理吗？**  
A：目前开发阶段不需要 Nginx，前端 dev 服务器自带代理。部署到服务器时再使用 Nginx。

---

### 📁 项目主要命令速查

- **前端开发**：`cd frontend && npm run dev`
- **前端构建**：`cd frontend && npm run build`（输出到 `dist/`）
- **后端启动**：`cd backend && mvnw.cmd spring-boot:run`
- **后端打包**：`cd backend && mvnw.cmd clean package -DskipTests`
- **爬虫运行**：先激活虚拟环境，再 `scrapy crawl dizzylab_spider`

---

去探索代码，开始发挥吧！遇到其他问题随时在群里沟通。