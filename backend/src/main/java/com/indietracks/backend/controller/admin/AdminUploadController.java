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

@RestController
@RequestMapping("/api/admin/upload")
public class AdminUploadController {

    private final MinioClient minioClient;

    @Value("${minio.bucket}")
    private String bucket;

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
                        .stream(is, file.getSize(), -1)
                        .contentType(file.getContentType())
                        .build()
                );
            }

            String url = "/minio/" + bucket + "/" + objectKey;
            return ResponseEntity.ok(Map.of("url", url, "object_key", objectKey));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("error", "上传失败: " + e.getMessage()));
        }
    }
}
