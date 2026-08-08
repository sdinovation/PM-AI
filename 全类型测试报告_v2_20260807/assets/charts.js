// assets/charts.js - 数分精灵全类型测试报告图表
(function() {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim() || '#2563eb';
  var accent2 = style.getPropertyValue('--accent2').trim() || '#dc2626';
  var accent3 = style.getPropertyValue('--accent3').trim() || '#16a34a';
  var accent4 = style.getPropertyValue('--accent4').trim() || '#f59e0b';
  var ink = style.getPropertyValue('--ink').trim() || '#1a1a2e';
  var muted = style.getPropertyValue('--muted').trim() || '#6c757d';
  var rule = style.getPropertyValue('--rule').trim() || '#dee2e6';
  var bg2 = style.getPropertyValue('--bg2').trim() || '#ffffff';

  // --- Chart 1: 各数分问题类型通过率 ---
  var chart1 = echarts.init(document.getElementById('chart-type-pass-rate'), null, { renderer: 'svg' });
  chart1.setOption({
    animation: false,
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, appendToBody: true },
    legend: { data: ['通过', '部分通过', '失败'], bottom: 0, textStyle: { color: muted } },
    grid: { left: 100, right: 30, top: 30, bottom: 60 },
    xAxis: { type: 'value', axisLabel: { color: muted }, splitLine: { lineStyle: { color: rule } } },
    yAxis: {
      type: 'category',
      data: ['排名分析','趋势分析','对比分析','分布分析','汇总统计','条件筛选','相关性分析','极值查询','多指标查询','占比分析','分组聚合','计数查询','HAVING条件','同比环比','基线对比'],
      axisLabel: { color: ink, fontSize: 12 },
      axisLine: { lineStyle: { color: rule } }
    },
    series: [
      { name: '通过', type: 'bar', stack: 'total', color: accent3, data: [0,0,0,0,0,0,3,0,0,0,0,7,0,0,0] },
      { name: '部分通过', type: 'bar', stack: 'total', color: accent4, data: [16,5,15,4,15,16,10,10,15,4,8,0,11,3,3] },
      { name: '失败', type: 'bar', stack: 'total', color: accent2, data: [0,7,1,10,1,0,0,1,0,0,0,0,0,0,0] }
    ]
  });
  window.addEventListener('resize', function() { chart1.resize(); });

  // --- Chart 2: 各数据集平均得分 ---
  var chart2 = echarts.init(document.getElementById('chart-dataset-score'), null, { renderer: 'svg' });
  chart2.setOption({
    animation: false,
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, appendToBody: true, formatter: function(p) { return p[0].name + ': ' + p[0].value + '%'; } },
    grid: { left: 120, right: 40, top: 20, bottom: 30 },
    xAxis: { type: 'value', max: 100, axisLabel: { color: muted, formatter: '{value}%' }, splitLine: { lineStyle: { color: rule } } },
    yAxis: {
      type: 'category',
      data: ['金融股票数据','医疗健康数据','能源消耗数据','电商销售数据','餐饮营收数据','教育成绩数据','天气气候数据','物流运输数据','房地产数据','HR薪资数据'],
      axisLabel: { color: ink, fontSize: 12 },
      axisLine: { lineStyle: { color: rule } },
      inverse: true
    },
    series: [{
      type: 'bar',
      data: [
        { value: 46, itemStyle: { color: accent2 } },
        { value: 54, itemStyle: { color: accent4 } },
        { value: 55, itemStyle: { color: accent4 } },
        { value: 56, itemStyle: { color: accent4 } },
        { value: 56, itemStyle: { color: accent4 } },
        { value: 56, itemStyle: { color: accent4 } },
        { value: 60, itemStyle: { color: accent4 } },
        { value: 59, itemStyle: { color: accent4 } },
        { value: 58, itemStyle: { color: accent4 } },
        { value: 61, itemStyle: { color: accent3 } }
      ],
      label: { show: true, position: 'right', formatter: '{c}%', color: ink, fontSize: 12, fontWeight: 600 },
      barWidth: 24
    }]
  });
  window.addEventListener('resize', function() { chart2.resize(); });

  // --- Chart 3: 问题类型分布 ---
  var chart3 = echarts.init(document.getElementById('chart-issue-types'), null, { renderer: 'svg' });
  chart3.setOption({
    animation: false,
    tooltip: { trigger: 'item', appendToBody: true, formatter: '{b}: {c} ({d}%)' },
    legend: { orient: 'vertical', right: 10, top: 'center', textStyle: { color: muted, fontSize: 12 } },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['40%', '50%'],
      data: [
        { value: 144, name: '意图不匹配', itemStyle: { color: accent2 } },
        { value: 31, name: '图表未生成', itemStyle: { color: accent4 } },
        { value: 8, name: 'SQL未生成', itemStyle: { color: '#8b5cf6' } },
        { value: 7, name: '图表类型错误', itemStyle: { color: '#06b6d4' } },
        { value: 2, name: '百分比缺失', itemStyle: { color: '#ec4899' } },
        { value: 1, name: '聚合缺失', itemStyle: { color: '#14b8a6' } },
        { value: 1, name: '对比缺失', itemStyle: { color: '#f97316' } }
      ],
      label: { color: ink, fontSize: 12 },
      itemStyle: { borderColor: bg2, borderWidth: 2 }
    }]
  });
  window.addEventListener('resize', function() { chart3.resize(); });

  // --- Chart 4: 关键错误模式统计 ---
  var chart4 = echarts.init(document.getElementById('chart-error-patterns'), null, { renderer: 'svg' });
  chart4.setOption({
    animation: false,
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, appendToBody: true },
    grid: { left: 180, right: 40, top: 20, bottom: 30 },
    xAxis: { type: 'value', axisLabel: { color: muted }, splitLine: { lineStyle: { color: rule } } },
    yAxis: {
      type: 'category',
      data: ['意图: DataQuery → ChartGen','状态污染 (SQL复用)','图表未生成','SQL未生成','图表类型错误','意图: Unclear','const变量错误','意图: RowLookup'],
      axisLabel: { color: ink, fontSize: 11 },
      axisLine: { lineStyle: { color: rule } },
      inverse: true
    },
    series: [{
      type: 'bar',
      data: [
        { value: 136, itemStyle: { color: accent2 } },
        { value: 81, itemStyle: { color: accent2 } },
        { value: 31, itemStyle: { color: accent4 } },
        { value: 8, itemStyle: { color: accent4 } },
        { value: 7, itemStyle: { color: accent4 } },
        { value: 4, itemStyle: { color: '#8b5cf6' } },
        { value: 3, itemStyle: { color: '#8b5cf6' } },
        { value: 1, itemStyle: { color: '#06b6d4' } }
      ],
      label: { show: true, position: 'right', color: ink, fontSize: 12, fontWeight: 600 },
      barWidth: 20
    }]
  });
  window.addEventListener('resize', function() { chart4.resize(); });

})();
