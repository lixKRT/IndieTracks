package com.indietracks.backend.config;

import com.baomidou.mybatisplus.annotation.DbType;
import com.baomidou.mybatisplus.core.MybatisConfiguration;
import com.baomidou.mybatisplus.extension.plugins.MybatisPlusInterceptor;
import com.baomidou.mybatisplus.extension.plugins.inner.PaginationInnerInterceptor;
import com.baomidou.mybatisplus.extension.spring.MybatisSqlSessionFactoryBean;
import org.apache.ibatis.session.SqlSessionFactory;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;

import javax.sql.DataSource;
import java.util.List;

/**
 * MyBatis-Plus 配置类
 * <p>
 * 负责配置 MyBatis-Plus 的核心组件，包括分页插件和自定义 SqlSessionFactory。
 * 本项目使用 PostgreSQL 数据库，需要特殊的类型处理器来处理数组类型。
 *
 * <h3>配置说明</h3>
 * <ul>
 *   <li><b>分页插件</b>：配置 PostgreSQL 方言的物理分页，支持 {@code LIMIT/OFFSET} 语法</li>
 *   <li><b>字段映射</b>：关闭自动下划线转驼峰，保持字段名与数据库列名一致（snake_case）</li>
 *   <li><b>类型处理器</b>：注册自定义 {@link StringListTypeHandler}，处理 PostgreSQL 的 text[] 数组类型</li>
 * </ul>
 *
 * <h3>为什么需要自定义 SqlSessionFactory？</h3>
 * <p>
 * 默认的 MyBatis-Plus 自动配置会创建 SqlSessionFactory，但无法注册自定义 TypeHandler。
 * 本项目需要将 PostgreSQL 的 text[] 映射为 Java 的 List&lt;String&gt;，
 * 因此必须手动创建并配置 SqlSessionFactory。
 * </p>
 *
 * @see com.indietracks.backend.handler.StringListTypeHandler
 * @author IndieTracks Team
 * @since 1.0
 */
@Configuration
public class MyBatisPlusConfig {

    /**
     * 配置 MyBatis-Plus 分页拦截器
     * <p>
     * 注册物理分页插件，指定数据库类型为 PostgreSQL。
     * 该插件会自动将 {@code SELECT * FROM table} 重写为
     * {@code SELECT * FROM table LIMIT x OFFSET y}。
     *
     * @return MybatisPlusInterceptor 实例，包含分页拦截器
     */
    @Bean
    public MybatisPlusInterceptor mybatisPlusInterceptor() {
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        interceptor.addInnerInterceptor(new PaginationInnerInterceptor(DbType.POSTGRE_SQL));
        return interceptor;
    }

    /**
     * 创建自定义 SqlSessionFactory
     * <p>
     * 手动配置 SqlSessionFactory 以支持：
     * <ul>
     *   <li>加载 XML Mapper 文件（classpath:mapper/*.xml）</li>
     *   <li>注册分页插件</li>
     *   <li>关闭驼峰命名转换（保持 snake_case 一致性）</li>
     *   <li>注册 PostgreSQL text[] 数组类型的处理器</li>
     * </ul>
     *
     * @param dataSource 数据源，由 Spring 自动注入
     * @return 配置完成的 SqlSessionFactory 实例
     * @throws Exception 如果资源加载或工厂创建失败
     */
    @Bean
    public SqlSessionFactory sqlSessionFactory(DataSource dataSource) throws Exception {
        MybatisSqlSessionFactoryBean factory = new MybatisSqlSessionFactoryBean();
        factory.setDataSource(dataSource);
        factory.setMapperLocations(
                new PathMatchingResourcePatternResolver().getResources("classpath:mapper/*.xml"));
        factory.setPlugins(mybatisPlusInterceptor());

        MybatisConfiguration configuration = new MybatisConfiguration();
        configuration.setMapUnderscoreToCamelCase(false); // 关闭自动下划线转驼峰，字段名与数据库列保持一致
        // 注册自定义 TypeHandler：PostgreSQL text[] <-> Java List<String>
        configuration.getTypeHandlerRegistry().register(List.class, org.apache.ibatis.type.JdbcType.ARRAY,
                com.indietracks.backend.handler.StringListTypeHandler.class);
        factory.setConfiguration(configuration);

        return factory.getObject();
    }
}
