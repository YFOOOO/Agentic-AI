"""
色彩无障碍检查模块
提供色盲友好的配色方案和对比度检查功能
"""

import colorsys
import numpy as np
from typing import List, Dict, Tuple, Optional
import matplotlib.colors as mcolors


class AccessibilityChecker:
    """色彩无障碍检查器"""
    
    # WCAG 2.1 对比度标准
    WCAG_AA_NORMAL = 4.5  # AA级别普通文本
    WCAG_AA_LARGE = 3.0   # AA级别大文本
    WCAG_AAA_NORMAL = 7.0 # AAA级别普通文本
    WCAG_AAA_LARGE = 4.5  # AAA级别大文本
    
    def __init__(self):
        """初始化无障碍检查器"""
        self.colorblind_safe_palettes = self._init_colorblind_safe_palettes()
        self.theme_palettes = self._init_theme_palettes()
    
    def _init_colorblind_safe_palettes(self) -> Dict[str, List[str]]:
        """初始化色盲友好调色板"""
        return {
            'viridis': ['#440154', '#31688e', '#35b779', '#fde725'],
            'cividis': ['#00224e', '#123570', '#3b496c', '#575d6d', '#707173', '#8a8678', '#a59c74', '#c3b369', '#e1cc55', '#fee838'],
            'wong': ['#000000', '#E69F00', '#56B4E9', '#009E73', '#F0E442', '#0072B2', '#D55E00', '#CC79A7'],
            'tol_bright': ['#EE6677', '#228833', '#4477AA', '#CCBB44', '#66CCEE', '#AA3377', '#BBBBBB'],
            'tol_muted': ['#CC6677', '#DDCC77', '#117733', '#332288', '#AA4499', '#44AA99', '#999933', '#882255', '#661100', '#6699CC'],
            'ibm': ['#648FFF', '#785EF0', '#DC267F', '#FE6100', '#FFB000', '#000000', '#FFFFFF']
        }
    
    def _init_theme_palettes(self) -> Dict[str, Dict[str, str]]:
        """初始化主题调色板"""
        return {
            'academic': {
                'primary': '#2E86AB',
                'secondary': '#A23B72', 
                'accent': '#F18F01',
                'background': '#FFFFFF',
                'text': '#2D3748'
            },
            'business': {
                'primary': '#1A365D',
                'secondary': '#2D3748',
                'accent': '#ED8936',
                'background': '#F7FAFC',
                'text': '#1A202C'
            },
            'high_contrast': {
                'primary': '#000000',
                'secondary': '#FFFFFF',
                'accent': '#FF0000',
                'background': '#FFFFFF',
                'text': '#000000'
            },
            'nature': {
                'primary': '#22543D',
                'secondary': '#2F855A',
                'accent': '#D69E2E',
                'background': '#F0FFF4',
                'text': '#1A202C'
            }
        }
    
    def hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """将十六进制颜色转换为RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """将RGB颜色转换为十六进制"""
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    def calculate_luminance(self, rgb: Tuple[int, int, int]) -> float:
        """计算颜色的相对亮度（WCAG标准）"""
        def gamma_correct(c):
            c = c / 255.0
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        
        r, g, b = [gamma_correct(c) for c in rgb]
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    def calculate_contrast_ratio(self, color1: str, color2: str) -> float:
        """计算两个颜色之间的对比度比值"""
        rgb1 = self.hex_to_rgb(color1)
        rgb2 = self.hex_to_rgb(color2)
        
        lum1 = self.calculate_luminance(rgb1)
        lum2 = self.calculate_luminance(rgb2)
        
        # 确保较亮的颜色在分子位置
        if lum1 < lum2:
            lum1, lum2 = lum2, lum1
        
        return (lum1 + 0.05) / (lum2 + 0.05)
    
    def check_wcag_compliance(self, foreground: str, background: str, 
                            text_size: str = 'normal', level: str = 'AA') -> Dict:
        """检查WCAG对比度合规性"""
        contrast_ratio = self.calculate_contrast_ratio(foreground, background)
        
        # 确定所需的最小对比度
        if level == 'AA':
            min_ratio = self.WCAG_AA_LARGE if text_size == 'large' else self.WCAG_AA_NORMAL
        else:  # AAA
            min_ratio = self.WCAG_AAA_LARGE if text_size == 'large' else self.WCAG_AAA_NORMAL
        
        return {
            'contrast_ratio': contrast_ratio,
            'required_ratio': min_ratio,
            'passes': contrast_ratio >= min_ratio,
            'level': level,
            'text_size': text_size
        }
    
    def simulate_colorblindness(self, hex_color: str, colorblind_type: str) -> str:
        """模拟色盲用户看到的颜色"""
        rgb = self.hex_to_rgb(hex_color)
        r, g, b = [c / 255.0 for c in rgb]
        
        # 色盲模拟矩阵（基于Brettel等人的研究）
        matrices = {
            'protanopia': np.array([  # 红色盲
                [0.567, 0.433, 0.000],
                [0.558, 0.442, 0.000],
                [0.000, 0.242, 0.758]
            ]),
            'deuteranopia': np.array([  # 绿色盲
                [0.625, 0.375, 0.000],
                [0.700, 0.300, 0.000],
                [0.000, 0.300, 0.700]
            ]),
            'tritanopia': np.array([  # 蓝色盲
                [0.950, 0.050, 0.000],
                [0.000, 0.433, 0.567],
                [0.000, 0.475, 0.525]
            ])
        }
        
        if colorblind_type not in matrices:
            return hex_color
        
        matrix = matrices[colorblind_type]
        rgb_array = np.array([r, g, b])
        simulated_rgb = np.dot(matrix, rgb_array)
        
        # 确保值在0-1范围内
        simulated_rgb = np.clip(simulated_rgb, 0, 1)
        
        # 转换回0-255范围并转为十六进制
        simulated_rgb_255 = tuple(int(c * 255) for c in simulated_rgb)
        return self.rgb_to_hex(simulated_rgb_255)
    
    def get_colorblind_safe_palette(self, palette_name: str = 'wong', 
                                  num_colors: Optional[int] = None) -> List[str]:
        """获取色盲友好的调色板"""
        if palette_name not in self.colorblind_safe_palettes:
            palette_name = 'wong'  # 默认使用Wong调色板
        
        palette = self.colorblind_safe_palettes[palette_name]
        
        if num_colors is None:
            return palette
        
        if num_colors <= len(palette):
            return palette[:num_colors]
        else:
            # 如果需要更多颜色，循环使用调色板
            extended_palette = []
            for i in range(num_colors):
                extended_palette.append(palette[i % len(palette)])
            return extended_palette
    
    def analyze_palette_accessibility(self, colors: List[str]) -> Dict:
        """分析调色板的无障碍性"""
        results = {
            'total_colors': len(colors),
            'pairwise_contrasts': [],
            'colorblind_simulation': {},
            'recommendations': []
        }
        
        # 计算所有颜色对之间的对比度
        for i, color1 in enumerate(colors):
            for j, color2 in enumerate(colors[i+1:], i+1):
                contrast = self.calculate_contrast_ratio(color1, color2)
                results['pairwise_contrasts'].append({
                    'color1': color1,
                    'color2': color2,
                    'contrast_ratio': contrast,
                    'sufficient_contrast': contrast >= 3.0
                })
        
        # 模拟不同类型色盲的效果
        colorblind_types = ['protanopia', 'deuteranopia', 'tritanopia']
        for cb_type in colorblind_types:
            results['colorblind_simulation'][cb_type] = [
                self.simulate_colorblindness(color, cb_type) for color in colors
            ]
        
        # 生成建议
        low_contrast_pairs = [pair for pair in results['pairwise_contrasts'] 
                            if not pair['sufficient_contrast']]
        
        if low_contrast_pairs:
            results['recommendations'].append(
                f"发现 {len(low_contrast_pairs)} 对颜色对比度不足，建议使用色盲友好调色板"
            )
        
        if len(colors) > 8:
            results['recommendations'].append(
                "颜色数量较多，建议考虑使用不同的形状或纹理来辅助区分"
            )
        
        return results
    
    def get_theme_colors(self, theme_name: str = 'academic') -> Dict[str, str]:
        """获取主题颜色方案"""
        if theme_name not in self.theme_palettes:
            theme_name = 'academic'
        
        return self.theme_palettes[theme_name].copy()
    
    def suggest_accessible_colors(self, base_color: str, num_colors: int = 5) -> List[str]:
        """基于基础颜色生成无障碍友好的颜色方案"""
        base_rgb = self.hex_to_rgb(base_color)
        base_hsv = colorsys.rgb_to_hsv(base_rgb[0]/255, base_rgb[1]/255, base_rgb[2]/255)
        
        colors = []
        
        # 生成不同饱和度和明度的颜色
        for i in range(num_colors):
            # 调整饱和度和明度以确保足够的对比度
            saturation = max(0.3, base_hsv[1] - 0.1 * i)
            value = min(0.9, base_hsv[2] + 0.15 * (i % 2) - 0.075)
            
            rgb = colorsys.hsv_to_rgb(base_hsv[0], saturation, value)
            rgb_255 = tuple(int(c * 255) for c in rgb)
            colors.append(self.rgb_to_hex(rgb_255))
        
        return colors


def demo_accessibility_checker():
    """演示无障碍检查功能"""
    checker = AccessibilityChecker()
    
    print("=== 色彩无障碍检查演示 ===\n")
    
    # 1. 测试对比度检查
    print("1. 对比度检查:")
    test_pairs = [
        ('#000000', '#FFFFFF', '黑白对比'),
        ('#FF0000', '#00FF00', '红绿对比'),
        ('#0072B2', '#FFFFFF', '蓝白对比'),
        ('#D55E00', '#000000', '橙黑对比')
    ]
    
    for fg, bg, desc in test_pairs:
        result = checker.check_wcag_compliance(fg, bg)
        status = "✅ 通过" if result['passes'] else "❌ 不通过"
        print(f"  {desc}: 对比度 {result['contrast_ratio']:.2f} {status}")
    
    # 2. 色盲友好调色板
    print("\n2. 色盲友好调色板:")
    wong_palette = checker.get_colorblind_safe_palette('wong', 6)
    print(f"  Wong调色板: {wong_palette}")
    
    # 3. 色盲模拟
    print("\n3. 色盲模拟 (#FF0000 红色):")
    test_color = '#FF0000'
    for cb_type in ['protanopia', 'deuteranopia', 'tritanopia']:
        simulated = checker.simulate_colorblindness(test_color, cb_type)
        print(f"  {cb_type}: {test_color} → {simulated}")
    
    # 4. 调色板分析
    print("\n4. 调色板无障碍性分析:")
    test_palette = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00']
    analysis = checker.analyze_palette_accessibility(test_palette)
    print(f"  测试调色板: {test_palette}")
    print(f"  颜色数量: {analysis['total_colors']}")
    print(f"  建议: {analysis['recommendations']}")
    
    # 5. 主题颜色
    print("\n5. 主题颜色方案:")
    academic_theme = checker.get_theme_colors('academic')
    print(f"  学术主题: {academic_theme}")
    
    print("\n=== 演示完成 ===")


if __name__ == "__main__":
    demo_accessibility_checker()