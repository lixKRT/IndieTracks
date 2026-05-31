package com.indietracks.backend.annotation;

import java.lang.annotation.*;

/**
 * 标注在 Controller 方法参数上，自动从 JWT 中提取当前用户 ID
 * 用法: public ResponseEntity<?> example(@CurrentUser Integer userId)
 */
@Target(ElementType.PARAMETER)
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface CurrentUser {
}
