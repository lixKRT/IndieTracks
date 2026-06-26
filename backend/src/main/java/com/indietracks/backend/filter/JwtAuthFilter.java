package com.indietracks.backend.filter;

import com.indietracks.backend.entity.User;
import com.indietracks.backend.mapper.UserMapper;
import com.indietracks.backend.util.JwtUtil;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Collections;
import java.util.List;

/**
 * JWT 认证过滤器。
 * <p>
 * 继承 {@link OncePerRequestFilter}，确保每次请求仅执行一次。从 HttpOnly Cookie 中提取 JWT Token，
 * 解析成功后查询用户角色并将认证信息写入 {@link SecurityContextHolder}，使后续的 Spring Security
 * 授权链（如 {@code @PreAuthorize}、URL 权限配置等）能够正常工作。
 * </p>
 *
 * <h3>认证流程</h3>
 * <ol>
 *   <li>从请求 Cookie 中提取名为 {@value #COOKIE_NAME} 的 JWT Token</li>
 *   <li>调用 {@link JwtUtil#isTokenValid(String)} 校验 Token 合法性（签名、过期时间）</li>
 *   <li>从 Token 中解析 userId，查询数据库获取用户角色</li>
 *   <li>构建 {@link UsernamePasswordAuthenticationToken} 写入 SecurityContext</li>
 * </ol>
 *
 * <h3>注意事项</h3>
 * <ul>
 *   <li>仅从 Cookie 提取 Token，不支持 Authorization Header（Bearer 方式）</li>
 *   <li>principal 存储的是 userId（{@link Integer}），而非 username</li>
 *   <li>未携带 Token 或 Token 无效时，过滤器静默放行，由后续授权配置决定是否拦截</li>
 * </ul>
 *
 * @see JwtUtil
 * @see org.springframework.security.authentication.UsernamePasswordAuthenticationToken
 */
@Component
public class JwtAuthFilter extends OncePerRequestFilter {

    /** Cookie 名称，与登录接口 {@code /api/auth/login} 写入的 HttpOnly Cookie 保持一致 */
    private static final String COOKIE_NAME = "indietracks_token";

    private final JwtUtil jwtUtil;
    private final UserMapper userMapper;

    /**
     * 构造注入。
     *
     * @param jwtUtil     JWT 工具类，用于解析和校验 Token
     * @param userMapper  用户 Mapper，用于根据 userId 查询用户角色
     */
    public JwtAuthFilter(JwtUtil jwtUtil, UserMapper userMapper) {
        this.jwtUtil = jwtUtil;
        this.userMapper = userMapper;
    }

    /**
     * 核心过滤逻辑：提取 Token、校验、构建认证对象。
     * <p>
     * 若 Token 有效，将 userId 作为 principal、用户角色作为 authorities 写入 SecurityContext；
     * 若 Token 不存在或无效，直接放行请求，由后续安全配置决定访问策略。
     * </p>
     *
     * @param request     当前 HTTP 请求
     * @param response    当前 HTTP 响应
     * @param filterChain 过滤器链，调用 {@code doFilter} 继续执行后续过滤器
     * @throws ServletException 如果过滤过程中发生 Servlet 异常
     * @throws IOException      如果过滤过程中发生 I/O 异常
     */
    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response,
                                    FilterChain filterChain) throws ServletException, IOException {
        String token = extractToken(request);

        if (token != null && jwtUtil.isTokenValid(token)) {
            Integer userId = jwtUtil.getUserId(token);

            // 查询用户角色
            User user = userMapper.selectById(userId);
            List<SimpleGrantedAuthority> authorities = Collections.emptyList();

            if (user != null && user.getUser_role() != null) {
                // Spring Security 要求角色前缀为 ROLE_
                authorities = List.of(new SimpleGrantedAuthority("ROLE_" + user.getUser_role()));
            }

            // principal 存 userId（非 username），credentials 为 null
            UsernamePasswordAuthenticationToken auth =
                    new UsernamePasswordAuthenticationToken(userId, null, authorities);
            SecurityContextHolder.getContext().setAuthentication(auth);
        }

        filterChain.doFilter(request, response);
    }

    /**
     * 从请求的 Cookie 数组中提取 JWT Token。
     * <p>
     * 仅匹配名为 {@value #COOKIE_NAME} 的 Cookie，不读取 Authorization Header。
     * </p>
     *
     * @param request 当前 HTTP 请求
     * @return Cookie 中的 Token 值；若未找到对应 Cookie 则返回 {@code null}
     */
    private String extractToken(HttpServletRequest request) {
        if (request.getCookies() != null) {
            for (Cookie cookie : request.getCookies()) {
                if (COOKIE_NAME.equals(cookie.getName())) {
                    return cookie.getValue();
                }
            }
        }
        return null;
    }
}
