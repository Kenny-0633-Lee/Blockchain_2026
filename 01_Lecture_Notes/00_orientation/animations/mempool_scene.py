from manim import *
import requests
import numpy as np

class MempoolToBlock(Scene):
    def construct(self):
        # 1. API 데이터 모사 (추후 실제 API 연동 가능)
        # fees = requests.get("https://mempool.space/api/mempool/recent").json() ...
        fees = [45, 38, 30, 25, 20, 15, 10, 8, 5, 2] 
        
        # 2. 타이틀 및 레이블 설정
        title = Text("Mempool Real-time Flow", font_size=36).to_edge(UP)
        mempool_label = Text("Mempool (Waiting)", font_size=24).shift(LEFT * 4 + UP * 2.5)
        block_label = Text("Next Block", font_size=24).shift(RIGHT * 4 + UP * 2.5)
        
        # 3. 박스 생성 (DashedRectangle 대신 DashedVMobject 사용)
        mempool_rect = Rectangle(width=4, height=5, color=GRAY).shift(LEFT * 4)
        mempool_box = DashedVMobject(mempool_rect, num_dashes=30).shift(LEFT * 4)
        block_box = Rectangle(width=3, height=4, color=GOLD).shift(RIGHT * 4)
        
        self.add(title, mempool_label, block_label, mempool_box, block_box)

        # 4. 트랜잭션 입자(Dots) 생성
        dots = VGroup()
        for fee in fees:
            # 수수료에 따라 색상 변경 (낮음: YELLOW -> 높음: RED)
            dot_color = interpolate_color(YELLOW, RED, fee/50)
            dot = Dot(radius=fee*0.005, color=dot_color)
            
            # 박스 내 무작위 위치 배치
            random_pos = mempool_box.get_center() + np.array([
                np.random.uniform(-1.5, 1.5),
                np.random.uniform(-2, 2),
                0
            ])
            dot.move_to(random_pos)
            dots.add(dot)

        self.play(LaggedStartMap(FadeIn, dots, lag_ratio=0.1))
        self.wait(1)

        # 5. 정렬 및 블록 삽입 애니메이션
        # 수수료 순으로 정렬되어 블록 안으로 들어가는 모습
        sorted_dots = dots.copy().arrange_in_grid(rows=5, cols=2, buff=0.3).move_to(block_box)
        
        self.play(
            ReplacementTransform(dots, sorted_dots),
            run_time=3,
            rate_func=exponential_decay
        )
        
        # 6. 블록 확정 효과 (Flash)
        self.play(
            block_box.animate.set_fill(GOLD, opacity=0.3),
            Flash(block_box, color=GOLD, line_length=0.5)
        )
        self.wait(2)