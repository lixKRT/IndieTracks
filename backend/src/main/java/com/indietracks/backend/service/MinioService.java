package com.indietracks.backend.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class MinioService {

    private static final Logger log = LoggerFactory.getLogger(MinioService.class);

    @Value("${minio.url-prefix}")
    private String urlPrefix;

    @Value("${minio.bucket}")
    private String bucket;

    public String getPresignedUrl(String objectKey) {
        if (objectKey == null || objectKey.isBlank()) {
            return null;
        }
        // url-prefix 由环境配置决定：
        // - dev: http://localhost:9000（直接访问 MinIO）
        // - prod: /minio（Nginx 代理）
        return urlPrefix + "/" + bucket + "/" + objectKey;
    }
}
