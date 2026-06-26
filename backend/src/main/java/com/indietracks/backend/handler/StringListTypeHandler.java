package com.indietracks.backend.handler;

import org.apache.ibatis.type.BaseTypeHandler;
import org.apache.ibatis.type.JdbcType;
import org.apache.ibatis.type.MappedJdbcTypes;
import org.apache.ibatis.type.MappedTypes;

import java.sql.*;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

/** MyBatis TypeHandler — 桥接 PostgreSQL text[] 与 Java List<String> */
@MappedTypes(List.class)      // 告诉 MyBatis 此 handler 处理 List 类型
@MappedJdbcTypes(JdbcType.ARRAY) // 对应 JDBC ARRAY 类型
public class StringListTypeHandler extends BaseTypeHandler<List<String>> {

    @Override
    public void setNonNullParameter(PreparedStatement ps, int i, List<String> parameter, JdbcType jdbcType) throws SQLException {
        Connection conn = ps.getConnection();
        Array array = conn.createArrayOf("varchar", parameter.toArray(new String[0])); // "varchar" 映射到 pg 的 text[]
        ps.setArray(i, array);
    }

    @Override
    public List<String> getNullableResult(ResultSet rs, String columnName) throws SQLException {
        return toList(rs.getArray(columnName));
    }

    @Override
    public List<String> getNullableResult(ResultSet rs, int columnIndex) throws SQLException {
        return toList(rs.getArray(columnIndex));
    }

    @Override
    public List<String> getNullableResult(CallableStatement cs, int columnIndex) throws SQLException {
        return toList(cs.getArray(columnIndex));
    }

    // null 安全：pg 数组为 null 时返回空集合而非 null
    private List<String> toList(Array array) throws SQLException {
        if (array == null) {
            return Collections.emptyList();
        }
        String[] values = (String[]) array.getArray();
        if (values == null) {
            return Collections.emptyList();
        }
        return new ArrayList<>(Arrays.asList(values));
    }
}
