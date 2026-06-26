package com.indietracks.backend.config;

import io.minio.MinioClient;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * MinIO 对象存储配置
 * <p>
 * 负责创建并配置 MinIO 客户端 Bean，用于管理平台中的文件存储（专辑封面、音频文件等）。
 * MinIO 是一个兼容 Amazon S3 API 的高性能对象存储服务。
 *
 * <h3>配置来源</h3>
 * <p>所有连接参数均从 {@code application.yml} 或环境变量中读取：</p>
 * <ul>
 *   <li>{@code minio.endpoint} — MinIO 服务地址（如 http://localhost:9000）</li>
 *   <li>{@code minio.access-key} — 访问密钥（类似 AWS Access Key ID）</li>
 *   <li>{@code minio.secret-key} — 秘密密钥（类似 AWS Secret Access Key）</li>
 * </ul>
 *
 * <h3>使用方式</h3>
 * <pre>
 * // 在 Service 中注入使用
 * {@code @Autowired}
 * private MinioClient minioClient;
 *
 * // 上传文件示例
 * minioClient.putObject(PutObjectArgs.builder()
 *     .bucket("albums")
 *     .object("covers/123.jpg")
 *     .stream(inputStream, size, -1)
 *     .build());
 * </pre>
 *
 * <h3>访问方式</h3>
 * <p>文件通过 Nginx 反向代理访问，不直接暴露 MinIO 端口。URL 格式：</p>
 * <p>{@code https://your-domain/minio/bucket-name/object-key}</p>
 *
 * @see com.indietracks.backend.service.MinioService
 * @author IndieTracks Team
 * @since 1.0
 */
@Configuration
public class MinioConfig {

    /**
     * MinIO 服务端点地址
     * <p>示例：http://localhost:9000</p>
     */
    @Value("${minio.endpoint}")
    private String endpoint;

    /**
     * MinIO 访问密钥
     * <p>用于身份验证，类似于 AWS 的 Access Key ID</p>
     */
    @Value("${minio.access-key}")
    private String accessKey;

    /**
     * MinIO 秘密密钥
     * <p>用于身份验证，类似于 AWS 的 Secret Access Key</p>
     */
    @Value("${minio.secret-key}")
    private String secretKey;

    /**
     * 创建 MinIO 客户端 Bean
     * <p>
     * 构建并配置 MinIO 客户端实例，该实例会被 Spring 容器管理为单例 Bean。
     * 客户端使用配置的端点地址和访问凭证进行初始化。
     *
     * @return MinIO 客户端实例，可用于文件的上传、下载、删除等操作
     */
    @Bean
    public MinioClient minioClient() {
        return MinioClient.builder()
                .endpoint(endpoint)
                .credentials(accessKey, secretKey)
                .build();
    }
}
