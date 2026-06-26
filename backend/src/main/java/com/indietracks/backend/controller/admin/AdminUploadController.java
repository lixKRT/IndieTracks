package com.indietracks.backend.controller.admin;

import io.minio.MinioClient;
import io.minio.PutObjectArgs;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.InputStream;
import java.util.Map;
import java.util.UUID;

/** 管理后台文件上传 — 封面、头像、Logo、音频，存储到 MinIO */
@RestController
@RequestMapping("/api/admin/upload")
public class AdminUploadController {

    private final MinioClient minioClient;

    @Value("${minio.bucket}")
    private String bucket; // MinIO 桶名，配置文件中定义

    public AdminUploadController(MinioClient minioClient) {
        this.minioClient = minioClient;
    }

    @PostMapping("/cover")
    public ResponseEntity<?> uploadCover(@RequestParam("file") MultipartFile file) {
        return uploadFile(file, "covers/");
    }

    @PostMapping("/avatar")
    public ResponseEntity<?> uploadAvatar(@RequestParam("file") MultipartFile file) {
        return uploadFile(file, "avatars/");
    }

    @PostMapping("/logo")
    public ResponseEntity<?> uploadLogo(@RequestParam("file") MultipartFile file) {
        return uploadFile(file, "logos/");
    }

    @PostMapping("/audio")
    public ResponseEntity<?> uploadAudio(@RequestParam("file") MultipartFile file) {
        return uploadFile(file, "audio/preview/");
    }

    /**
     * 通用文件上传逻辑
     * @param prefix MinIO 对象 Key 前缀，如 "covers/"、"audio/preview/"
     * @return url — Nginx 代理访问路径；object_key — MinIO 对象 Key，前端拼接完整地址
     */
    private ResponseEntity<?> uploadFile(MultipartFile file, String prefix) {
        try {
            String originalFilename = file.getOriginalFilename();
            String extension = "";
            if (originalFilename != null && originalFilename.contains(".")) {
                extension = originalFilename.substring(originalFilename.lastIndexOf("."));
            }
            String objectKey = prefix + UUID.randomUUID().toString() + extension;

            try (InputStream is = file.getInputStream()) {
                minioClient.putObject(
                    PutObjectArgs.builder()
                        .bucket(bucket)
                        .object(objectKey)
                        .stream(is, file.getSize(), -1) // -1 表示未知分片大小，由 SDK 自动处理
                        .contentType(file.getContentType())
                        .build()
                );
            }

            String url = "/minio/" + bucket + "/" + objectKey; // Nginx 代理路径，非 MinIO 直连地址
            return ResponseEntity.ok(Map.of("url", url, "object_key", objectKey));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("error", "上传失败: " + e.getMessage()));
        }
    }
}
