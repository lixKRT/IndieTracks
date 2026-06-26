package com.indietracks.backend.config;

import com.indietracks.backend.filter.JwtAuthFilter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

/** Spring Security 配置 — JWT 无状态认证，基于角色的接口权限控制 */
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    private final JwtAuthFilter jwtAuthFilter;

    public SecurityConfig(JwtAuthFilter jwtAuthFilter) {
        this.jwtAuthFilter = jwtAuthFilter;
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable()) // JWT 无状态认证，无需 CSRF 防护
            .sessionManagement(sm -> sm.sessionCreationPolicy(SessionCreationPolicy.STATELESS)) // 不创建 HttpSession，认证由 JWT 完成
            .authorizeHttpRequests(auth -> auth
                // 公开接口
                .requestMatchers("/api/auth/register", "/api/auth/login").permitAll()
                .requestMatchers(HttpMethod.GET, "/api/albums/**").permitAll()
                .requestMatchers(HttpMethod.GET, "/api/circles/**").permitAll()
                .requestMatchers(HttpMethod.GET, "/api/tags").permitAll()
                .requestMatchers(HttpMethod.GET, "/api/users/**").permitAll()
                // 需要登录的接口
                .requestMatchers("/api/auth/**").authenticated()
                .requestMatchers(HttpMethod.POST, "/api/favorites/**").authenticated()
                .requestMatchers(HttpMethod.DELETE, "/api/favorites/**").authenticated()
                .requestMatchers(HttpMethod.POST, "/api/circle-follows/**").authenticated()
                .requestMatchers(HttpMethod.DELETE, "/api/circle-follows/**").authenticated()
                .requestMatchers(HttpMethod.POST, "/api/user-follows/**").authenticated()
                .requestMatchers(HttpMethod.DELETE, "/api/user-follows/**").authenticated()
                .requestMatchers(HttpMethod.POST, "/api/albums/*/comments").authenticated()
                .requestMatchers(HttpMethod.PUT, "/api/comments/**").authenticated()
                .requestMatchers(HttpMethod.DELETE, "/api/comments/**").authenticated()
                .requestMatchers(HttpMethod.POST, "/api/purchases/**").authenticated()
                .requestMatchers(HttpMethod.GET, "/api/purchases").authenticated()
                .requestMatchers("/api/cart/**").authenticated()
                // 管理接口 - 仅 staff 可访问（必须在通用规则之前）
                .requestMatchers("/api/admin/circles/**").hasAuthority("ROLE_staff")
                .requestMatchers("/api/admin/users/**").hasAuthority("ROLE_staff")
                // 管理接口 - 需要 pro 或 staff 角色
                .requestMatchers("/api/admin/**").hasAnyAuthority("ROLE_pro", "ROLE_staff")
                // 其他请求放行
                .anyRequest().permitAll()
            )
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
