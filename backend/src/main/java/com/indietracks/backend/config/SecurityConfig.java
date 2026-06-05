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
            .csrf(csrf -> csrf.disable())
            .sessionManagement(sm -> sm.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
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
