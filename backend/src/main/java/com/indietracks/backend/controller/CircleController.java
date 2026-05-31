package com.indietracks.backend.controller;

import com.indietracks.backend.dto.CircleDetail;
import com.indietracks.backend.dto.CircleListItem;
import com.indietracks.backend.service.CircleService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/circles")
public class CircleController {

    private final CircleService circleService;

    public CircleController(CircleService circleService) {
        this.circleService = circleService;
    }

    @GetMapping
    public ResponseEntity<Map<String, Object>> getCircles() {
        List<CircleListItem> circles = circleService.getCircleList();
        Map<String, Object> response = new HashMap<>();
        response.put("data", circles);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/{id}")
    public ResponseEntity<CircleDetail> getCircle(@PathVariable Integer id) {
        CircleDetail detail = circleService.getCircleDetail(id);
        if (detail == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(detail);
    }
}
