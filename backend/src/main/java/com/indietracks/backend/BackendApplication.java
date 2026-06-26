package com.indietracks.backend;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * IndieTracks 后端应用启动类
 * <p>
 * 作为整个 Spring Boot 应用的入口点，负责：
 * <ul>
 *   <li>启动 Spring IoC 容器，自动扫描并注册所有组件（Controller、Service、Mapper 等）</li>
 *   <li>通过 {@code @MapperScan} 自动扫描 MyBatis Mapper 接口，无需逐个标注 {@code @Mapper}</li>
 *   <li>触发自动配置（数据库连接池、Web 服务器、安全框架等）</li>
 * </ul>
 *
 * <h3>技术栈说明</h3>
 * <ul>
 *   <li>Spring Boot 4 + Java 25</li>
 *   <li>MyBatis-Plus（通过 {@code @MapperScan} 注册 Mapper）</li>
 *   <li>内嵌 Jetty 服务器</li>
 * </ul>
 *
 * @author IndieTracks Team
 * @since 1.0
 */
@SpringBootApplication
@MapperScan("com.indietracks.backend.mapper")
public class BackendApplication {

    /**
     * 应用主入口方法
     * <p>
     * 通过 {@link SpringApplication#run(Class, String[])} 启动整个 Spring Boot 应用。
     * 启动过程中会完成以下工作：
     * <ol>
     *   <li>创建并刷新 Spring 应用上下文</li>
     *   <li>启动内嵌 Jetty Web 服务器（默认端口 8080）</li>
     *   <li>初始化数据库连接池</li>
     *   <li>注册所有 REST API 端点</li>
     * </ol>
     *
     * @param args 命令行参数，可通过 {@code --server.port=9090} 等方式覆盖配置
     */
    public static void main(String[] args) {
        SpringApplication.run(BackendApplication.class, args);
    }

}
