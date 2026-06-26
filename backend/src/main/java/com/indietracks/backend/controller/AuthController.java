package com.indietracks.backend.controller;

import com.indietracks.backend.annotation.CurrentUser;
import com.indietracks.backend.dto.LoginRequest;
import com.indietracks.backend.dto.RegisterRequest;
import com.indietracks.backend.dto.UserDTO;
import com.indietracks.backend.service.AuthService;
import com.indietracks.backend.service.MinioService;
import com.indietracks.backend.util.UrlPresignHelper;
import io.minio.MinioClient;
import io.minio.PutObjectArgs;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.InputStream;
import java.util.Map;
import java.util.UUID;

/** 认证相关接口 — 注册、登录、登出、用户信息、头像上传 */
@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private static final String COOKIE_NAME = "indietracks_token";
    private static final int COOKIE_MAX_AGE = 7 * 24 * 3600;            // 7 天（秒）
    private static final int COOKIE_REMEMBER_ME_MAX_AGE = 30 * 24 * 3600; // 30 天（秒）

    private final AuthService authService;
    private final MinioService minioService;
    private final MinioClient minioClient;
    private final UrlPresignHelper urlPresign;

    @Value("${minio.bucket}")
    private String bucket; // MinIO 存储桶名称

    public AuthController(AuthService authService, MinioService minioService,
                          MinioClient minioClient, UrlPresignHelper urlPresign) {
        this.authService = authService;
        this.minioService = minioService;
        this.minioClient = minioClient;
        this.urlPresign = urlPresign;
    }

    @PostMapping("/register")
    public ResponseEntity<?> register(@Valid @RequestBody RegisterRequest req, HttpServletResponse response) {
        UserDTO user = authService.register(req);
        String token = authService.generateToken(user, false);
        setCookie(response, token, COOKIE_MAX_AGE);
        return ResponseEntity.ok(user);
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@Valid @RequestBody LoginRequest req, HttpServletResponse response) {
        UserDTO user = authService.login(req);
        int maxAge = req.isRemember_me() ? COOKIE_REMEMBER_ME_MAX_AGE : COOKIE_MAX_AGE;
        String token = authService.generateToken(user, req.isRemember_me());
        setCookie(response, token, maxAge);
        urlPresign.presignUserDTO(user);
        return ResponseEntity.ok(user);
    }

    @PostMapping("/logout")
    public ResponseEntity<?> logout(HttpServletResponse response) {
        Cookie cookie = new Cookie(COOKIE_NAME, "");
        cookie.setHttpOnly(true);
        cookie.setPath("/");
        cookie.setMaxAge(0);
        response.addCookie(cookie);
        return ResponseEntity.ok(Map.of("message", "已登出"));
    }

    @GetMapping("/me")
    public ResponseEntity<?> me(@CurrentUser Integer userId) {
        if (userId == null) {
            return ResponseEntity.status(401).body(Map.of("error", "未登录"));
        }
        UserDTO user = authService.getUserById(userId);
        if (user == null) {
            return ResponseEntity.status(401).body(Map.of("error", "用户不存在"));
        }
        // getUserById 内部已做预签名
        return ResponseEntity.ok(user);
    }

    @PostMapping("/avatar")
    public ResponseEntity<?> uploadAvatar(@RequestParam("file") MultipartFile file,
                                          @CurrentUser Integer userId) {
        try {
            String ext = file.getOriginalFilename();
            ext = ext != null && ext.contains(".") ? ext.substring(ext.lastIndexOf(".")) : ".jpg";
            // MinIO 对象 Key，格式 avatars/{userId}_{uuid}.{ext}
            String objectKey = "avatars/" + userId + "_" + UUID.randomUUID() + ext;

            try (InputStream is = file.getInputStream()) {
                minioClient.putObject(
                        PutObjectArgs.builder()
                                .bucket(bucket)
                                .object(objectKey)
                                .stream(is, file.getSize(), -1)
                                .contentType(file.getContentType())
                                .build()
                );
            }

            authService.updateAvatar(userId, objectKey);
            String url = minioService.getPresignedUrl(objectKey);
            return ResponseEntity.ok(Map.of("avatar_url", url));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("error", "上传失败: " + e.getMessage()));
        }
    }

    private void setCookie(HttpServletResponse response, String token, int maxAge) {
        Cookie cookie = new Cookie(COOKIE_NAME, token);
        cookie.setHttpOnly(true);
        cookie.setPath("/");
        cookie.setMaxAge(maxAge);
        response.addCookie(cookie);
    }
}
