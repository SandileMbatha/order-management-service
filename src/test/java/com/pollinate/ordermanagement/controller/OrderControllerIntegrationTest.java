package com.pollinate.ordermanagement.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.pollinate.ordermanagement.dto.OrderItemRequest;
import com.pollinate.ordermanagement.dto.OrderRequest;
import com.pollinate.ordermanagement.dto.ProductRequest;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;
import java.util.List;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
class OrderControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    private static final String API_KEY = "my-secret-api-key-2024";

    private Long productId;

    @BeforeEach
    void setUp() throws Exception {
        ProductRequest productRequest = new ProductRequest("Order Test Product", "For order tests", new BigDecimal("100.00"));

        String response = mockMvc.perform(post("/api/products")
                        .header("X-API-Key", API_KEY)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(productRequest)))
                .andReturn().getResponse().getContentAsString();

        productId = objectMapper.readTree(response).get("id").asLong();
    }

    @Test
    void shouldCreateOrderAndCalculateTotal() throws Exception {
        OrderRequest request = new OrderRequest(List.of(
                new OrderItemRequest(productId, 3)  // 3 x 100 = 300
        ));

        String response = mockMvc.perform(post("/api/orders")
                        .header("X-API-Key", API_KEY)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.totalPrice").value(300.00))
                .andExpect(jsonPath("$.items").isArray())
                .andExpect(jsonPath("$.items[0].quantity").value(3))
                .andReturn().getResponse().getContentAsString();

        Long orderId = objectMapper.readTree(response).get("id").asLong();

        mockMvc.perform(get("/api/orders/{id}", orderId)
                        .header("X-API-Key", API_KEY))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(orderId));
    }

    @Test
    void shouldRejectOrder_whenProductDoesNotExist() throws Exception {
        OrderRequest request = new OrderRequest(List.of(
                new OrderItemRequest(99999L, 1)
        ));

        mockMvc.perform(post("/api/orders")
                        .header("X-API-Key", API_KEY)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.missingProductIds").isArray())
                .andExpect(jsonPath("$.missingProductIds[0]").value(99999));
    }

    @Test
    void shouldRejectOrder_whenItemsEmpty() throws Exception {
        OrderRequest request = new OrderRequest(List.of());

        mockMvc.perform(post("/api/orders")
                        .header("X-API-Key", API_KEY)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest());
    }

    @Test
    void shouldListOrdersWithPagination() throws Exception {
        mockMvc.perform(get("/api/orders?page=0&size=5")
                        .header("X-API-Key", API_KEY))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.pageable").exists());
    }
}
