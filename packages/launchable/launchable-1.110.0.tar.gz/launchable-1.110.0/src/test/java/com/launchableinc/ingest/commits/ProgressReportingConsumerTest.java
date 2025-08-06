package com.launchableinc.ingest.commits;

import com.google.common.truth.Truth;
import org.junit.Test;

import java.time.Duration;
import java.util.ArrayList;
import java.util.List;

public class ProgressReportingConsumerTest {
    @Test
    public void basic() {
        List<String> done = new ArrayList<>();
        try (ProgressReportingConsumer<String> x = new ProgressReportingConsumer<>(s -> {done.add(s);sleep();}, String::valueOf, Duration.ofMillis(100))) {
            for (int i = 0; i < 100; i++) {
                x.accept("item " + i);
            }
        }
        Truth.assertThat(done.size()).isEqualTo(100);
    }

    private static void sleep() {
        try {
            Thread.sleep(10);
        } catch (InterruptedException e) {
            throw new UnsupportedOperationException();
        }
    }
}
