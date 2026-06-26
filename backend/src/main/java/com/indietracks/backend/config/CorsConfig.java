package com.indietracks.backend.config;

import jakarta.servlet.http.HttpServletRequest;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.util.List;

/**
 * 跨域资源共享（CORS）配置
 * <p>
 * 解决浏览器同源策略限制，允许前端 Vue 开发服务器（运行在不同端口）访问后端 API。
 * 本项目采用 HttpOnly Cookie + JWT 认证方案，因此必须开启 {@code allowCredentials}。
 *
 * <h3>安全策略说明</h3>
 * <ul>
 *   <li><b>allowedOriginPatterns</b>：仅允许 localhost 任意端口，生产环境需改为具体域名</li>
 *   <li><b>allowCredentials(true)</b>：允许携带 Cookie，这是 HttpOnly JWT 认证的前提</li>
 *   <li><b>maxAge(3600)</b>：preflight 预检请求缓存 1 小时，减少 OPTIONS 请求开销</li>
 * </ul>
 *
 * <h3>请求流程</h3>
 * <pre>
 * 前端 (localhost:5173) ──OPTIONS preflight──▶ 后端 (localhost:8080)
 *                        ◀──200 + CORS 头────
 *                        ──GET /api/xxx + Cookie──▶
 *                        ◀──JSON 响应 + Set-Cookie──
 * </pre>
 *
 * @see WebMvcConfigurer#addCorsMappings(CorsRegistry)
 * @author IndieTracks Team
 * @since 1.0
 */
@Configuration
public class CorsConfig implements WebMvcConfigurer {

    /**
     * 配置 CORS 策略
     * <p>
     * 对所有 /api/** 路径下的接口启用跨域支持。
     *
     * @param registry CORS 注册器，用于添加跨域映射规则
     */
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
                .allowedOriginPatterns("http://localhost:*") // 允许任意本地端口，适配前端 dev server 随机端口
                .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                .allowedHeaders("*")
                .allowCredentials(true) // 允许跨域携带 Cookie（HttpOnly JWT 认证需要）
                .maxAge(3600); // preflight 缓存 1 小时，减少 OPTIONS 请求
    }
}
