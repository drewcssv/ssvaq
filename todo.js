
var markers = [
        ['BackpAQ 1', 37.875290, -122.541390, '1059654', '/fields/2/','last.json?','api_key=DZ07N6EQQM0GEUPE', '811 Smith Road MV'], 
        ['BackpAQ 2', 37.875293, -122.541396, '1060405', '/fields/2/','last.json?','api_key=BNY857AMT8UZ8E9X', '811 Smith Road MV'], 
        ['BackpAQ 3', 37.875293, -122.541399, '1150280', '/fields/2/','last.json?','api_key=BMP7BLV51DNQCHQC', '811 Smith Road MV'], // my sensor
        ['BackpAQ 4', 37.875293, -122.541399, '1150280', '/fields/2/','last.json?','api_key=CCP02S8KPW8A6BDI', '811 Smith Road MV'],
        ['BAQ Labs PA', 37.875280, -122.541396, '720433', '/fields/2/','last.json?','api_key=CCP02S8KPW8A6BDI', '811 Smith Rd BackpAQ Labs'] // was SSV 2U
        ];

  // Build Info Window Content  Keep parallel with above marker list 
     var infoWindowContent = [
    // BPQ1  
    ['<div class="info_content">' +
    '<h3>' + markers[0][0] +'</h3>' +
    '<p>BackpAQ Monitor ' + markers[0][0] + ' is located at ' + markers[0][7] + '.</p>' + '</div>'],
    // BPQ2
    ['<div class="info_content">' +
    '<h3>' + markers[1][0]+ '</h3>' +
    '<p>BackpAQ Monitor ' + markers[1][0] + ' is located at  ' + markers[1][7] + '.</p>' +
    '</div>'],
    // BPQ3
    ['<div class="info_content">' +
    '<h3>' + markers[2][0] + '</h3>' +
    '<p>BackpAQ Monitor ' + markers[2][0] + ' is located at  ' + markers[2][7] + '</p>' +
    '</div>'],
    // BPQ4 
    ['<div class="info_content">' +
    '<h3>' + markers[3][0] + '</h3>' +
    '<p>BackpAQ Monitor ' + markers[3][0] + ' is located at  ' + markers[3][7] + '</p>' +
    '</div>'],  
    // BAQ Labs PA Sensor
    ['<div class="info_content">' +
    '<h3>' + markers[4][0] + '</h3>' +
    '<p>Purple Air sensor ' + markers[4][0] + ' is located at  ' + markers[4][7] + '</p>' +
    '</div>']   
   ]; //infowindow content array