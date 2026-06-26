package com.indietracks.backend.util;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;

/**
 * JWT 工具类，封装 Token 的生成、解析与校验逻辑。
 * <p>
 * 基于 <a href="https://github.com/jwtk/jjwt">JJWT</a> 库实现，使用 HMAC-SHA 签名算法。
 * 密钥和过期时间通过 {@code application.yml} 中的 {@code jwt.*} 配置项注入。
 * </p>
 *
 * <h3>Token 结构</h3>
 * <ul>
 *   <li>{@code sub}（subject）— 用户 ID（Integer 转为字符串）</li>
 *   <li>{@code username} — 用户名（自定义 claim）</li>
 *   <li>{@code iat}（issued at）— 签发时间</li>
 *   <li>{@code exp}（expiration）— 过期时间，根据是否"记住我"使用不同有效期</li>
 * </ul>
 *
 * <h3>配置示例（application.yml）</h3>
 * <pre>{@code
 * jwt:
 *   secret: "your-256-bit-secret-key-here..."
 *   expiration: 3600              # 普通登录 1 小时（秒）
 *   remember-me-expiration: 604800 # 记住我 7 天（秒）
 * }</pre>
 *
 * @see com.indietracks.backend.filter.JwtAuthFilter
 */
@Component
public class JwtUtil {

    /** HMAC-SHA 签名密钥，由配置项 {@code jwt.secret} 生成 */
    private final SecretKey key;

    /** 普通登录过期时间，单位：秒 */
    private final long expiration;

    /** "记住我"过期时间，单位：秒 */
    private final long rememberMeExpiration;

    /**
     * 构造注入，从配置文件读取 JWT 密钥和过期时间。
     *
     * @param secret               HMAC-SHA 密钥字符串（至少 256 位）
     * @param expiration           普通登录的过期时间（秒）
     * @param rememberMeExpiration 勾选"记住我"时的过期时间（秒）
     */
    public JwtUtil(@Value("${jwt.secret}") String secret,
                   @Value("${jwt.expiration}") long expiration,
                   @Value("${jwt.remember-me-expiration}") long rememberMeExpiration) {
        this.key = Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
        this.expiration = expiration;
        this.rememberMeExpiration = rememberMeExpiration;
    }

    /**
     * 生成 JWT Token。
     * <p>
     * 根据 {@code rememberMe} 参数选择不同的过期时间。Token 中包含 userId（subject）、
     * username（自定义 claim）、签发时间和过期时间。
     * </p>
     *
     * @param userId     用户 ID，写入 Token 的 subject 字段
     * @param username   用户名，写入自定义 claim
     * @param rememberMe 是否"记住我"，决定使用普通过期时间还是延长过期时间
     * @return 签名后的 JWT Token 字符串
     */
    public String generateToken(Integer userId, String username, boolean rememberMe) {
        long exp = rememberMe ? rememberMeExpiration : expiration;
        return Jwts.builder()
                .subject(String.valueOf(userId))
                .claim("username", username)
                .issuedAt(new Date())
                .expiration(new Date(System.currentTimeMillis() + exp * 1000))
                .signWith(key)
                .compact();
    }

    /**
     * 解析并验证 JWT Token，返回其 Claims 载荷。
     * <p>
     * 此方法会验证签名和 Token 结构，若签名不匹配或格式错误将抛出异常。
     * </p>
     *
     * @param token JWT Token 字符串
     * @return 解析后的 {@link Claims} 对象，包含 subject、过期时间等信息
     * @throws io.jsonwebtoken.JwtException 如果 Token 签名无效或格式错误
     * @throws io.jsonwebtoken.ExpiredJwtException 如果 Token 已过期
     */
    public Claims parseToken(String token) {
        return Jwts.parser()
                .verifyWith(key)
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }

    /**
     * 从 Token 中提取用户 ID。
     * <p>
     * 用户 ID 存储在 Token 的 subject（{@code sub}）字段中。
     * </p>
     *
     * @param token JWT Token 字符串
     * @return 用户 ID
     * @throws io.jsonwebtoken.JwtException 如果 Token 无效
     * @throws NumberFormatException         如果 subject 无法转为 Integer
     */
    public Integer getUserId(String token) {
        return Integer.valueOf(parseToken(token).getSubject());
    }

    /**
     * 校验 Token 是否有效（签名正确且未过期）。
     * <p>
     * 任何解析异常（过期、篡改、格式错误等）均视为无效，返回 {@code false}。
     * </p>
     *
     * @param token JWT Token 字符串
     * @return {@code true} 表示 Token 有效；{@code false} 表示无效或已过期
     */
    public boolean isTokenValid(String token) {
        try {
            Claims claims = parseToken(token);
            return !claims.getExpiration().before(new Date());
        } catch (Exception e) {
            return false;
        }
    }
}
