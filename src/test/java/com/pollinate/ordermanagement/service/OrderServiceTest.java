package com.pollinate.ordermanagement.service;

import com.pollinate.ordermanagement.dto.OrderItemRequest;
import com.pollinate.ordermanagement.dto.OrderRequest;
import com.pollinate.ordermanagement.dto.OrderResponse;
import com.pollinate.ordermanagement.entity.Order;
import com.pollinate.ordermanagement.entity.OrderItem;
import com.pollinate.ordermanagement.entity.Product;
import com.pollinate.ordermanagement.exception.InvalidOrderException;
import com.pollinate.ordermanagement.exception.ResourceNotFoundException;
import com.pollinate.ordermanagement.repository.OrderRepository;
import com.pollinate.ordermanagement.repository.ProductRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class OrderServiceTest {

    @Mock
    private OrderRepository orderRepository;

    @Mock
    private ProductRepository productRepository;

    @InjectMocks
    private OrderService orderService;

    @Test
    void createOrder_shouldCalculateTotalAndSave() {
        Product laptop = Product.builder().id(1L).name("Laptop").price(new BigDecimal("1000.00")).createdAt(LocalDateTime.now()).build();
        Product mouse = Product.builder().id(2L).name("Mouse").price(new BigDecimal("25.00")).createdAt(LocalDateTime.now()).build();

        when(productRepository.findAllById(any())).thenReturn(List.of(laptop, mouse));
        when(orderRepository.save(any(Order.class))).thenAnswer(invocation -> {
            Order order = invocation.getArgument(0);
            order.setId(1L);
            order.setCreatedAt(LocalDateTime.now());
            return order;
        });

        OrderRequest request = new OrderRequest(List.of(
                new OrderItemRequest(1L, 2),  // 2 laptops = 2000
                new OrderItemRequest(2L, 3)   // 3 mice = 75
        ));

        OrderResponse response = orderService.createOrder(request);

        assertThat(response.id()).isEqualTo(1L);
        assertThat(response.totalPrice()).isEqualByComparingTo("2075.00");
        assertThat(response.items()).hasSize(2);
        verify(orderRepository).save(any(Order.class));
    }

    @Test
    void createOrder_shouldRejectWhenProductNotFound() {
        Product laptop = Product.builder().id(1L).name("Laptop").price(new BigDecimal("1000.00")).createdAt(LocalDateTime.now()).build();
        when(productRepository.findAllById(any())).thenReturn(List.of(laptop));

        OrderRequest request = new OrderRequest(List.of(
                new OrderItemRequest(1L, 1),
                new OrderItemRequest(99L, 1)
        ));

        assertThatThrownBy(() -> orderService.createOrder(request))
                .isInstanceOf(InvalidOrderException.class)
                .hasMessageContaining("99");
    }

    @Test
    void createOrder_shouldRejectWhenMultipleProductsMissing() {
        when(productRepository.findAllById(any())).thenReturn(List.of());

        OrderRequest request = new OrderRequest(List.of(
                new OrderItemRequest(10L, 1),
                new OrderItemRequest(20L, 1)
        ));

        assertThatThrownBy(() -> orderService.createOrder(request))
                .isInstanceOf(InvalidOrderException.class)
                .extracting(e -> ((InvalidOrderException) e).getMissingProductIds())
                .asList()
                .containsExactly(10L, 20L);
    }

    @Test
    void getOrderById_shouldReturnOrder_whenExists() {
        Product product = Product.builder().id(1L).name("Phone").price(new BigDecimal("500.00")).createdAt(LocalDateTime.now()).build();
        OrderItem item = OrderItem.builder().id(1L).product(product).quantity(1).lineTotal(new BigDecimal("500.00")).build();
        Order order = Order.builder().id(1L).totalPrice(new BigDecimal("500.00")).createdAt(LocalDateTime.now()).items(List.of(item)).build();

        when(orderRepository.findById(1L)).thenReturn(Optional.of(order));

        OrderResponse response = orderService.getOrderById(1L);

        assertThat(response.id()).isEqualTo(1L);
        assertThat(response.totalPrice()).isEqualByComparingTo("500.00");
    }

    @Test
    void getOrderById_shouldThrowException_whenNotFound() {
        when(orderRepository.findById(99L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> orderService.getOrderById(99L))
                .isInstanceOf(ResourceNotFoundException.class)
                .hasMessageContaining("99");
    }
}
