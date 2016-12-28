

var target = document.getElementsByClassName('product-list')[0];

var str = '<i>领券<br>减30</i><span class="money02">佣金31.25%</span><a href="#"><img src="images/product-detail.png" alt=""></a><a href="#"><h4>新品大促秋冬装棉衣男长款加厚 情侣棉衣外套潮</h4></a><div class="clearfix price"><strong>￥129.00</strong><small>售出<em>1325</em>件</small></div><div class="links flex"><a href="#">立即推广</a><a href="ios:showDetail:hello world" style="border-right:0">查看商品</a></div>';


for(var i = 0; i < 8; i++){
    var item = document.createElement("div");
    var att = document.createAttribute("class");
    att.value = "product-item";
    item.setAttributeNode(att);
    item.innerHTML = str;
    target.append(item);
}


