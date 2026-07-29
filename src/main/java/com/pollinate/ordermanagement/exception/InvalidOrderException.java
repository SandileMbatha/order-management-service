package com.pollinate.ordermanagement.exception;

import java.util.List;

public class InvalidOrderException extends RuntimeException {
    private final List<Long> missingProductIds;

    public InvalidOrderException(List<Long> missingProductIds) {
        super("Products not found with IDs: " + missingProductIds);
        this.missingProductIds = missingProductIds;
    }

    public List<Long> getMissingProductIds() {
        return missingProductIds;
    }
}
