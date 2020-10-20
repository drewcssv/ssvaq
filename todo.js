
var markers = [
        ['BackpAQ 1', 37.875290, -122.541390, '1059654', '/fields/2/','last.json?','api_key=DZ07N6EQQM0GEUPE', '811 Smith Road MV', 'BackpAQ'], 
        ['BackpAQ 2', 37.875293, -122.541396, '1060405', '/fields/2/','last.json?','api_key=BNY857AMT8UZ8E9X', '811 Smith Road MV', 'BackpAQ'], 
        ['BackpAQ 3', 37.875293, -122.541399, '1150280', '/fields/2/','last.json?','api_key=BMP7BLV51DNQCHQC', '811 Smith Road MV', 'BackpAQ'], // my sensor
        ['BackpAQ 4', 37.875293, -122.541399, '1150280', '/fields/2/','last.json?','api_key=CCP02S8KPW8A6BDI', '811 Smith Road MV', 'BackpAQ'],
        ['BAQ Labs PA', 37.875280, -122.541396, '720433', '/fields/2/','last.json?','api_key=CCP02S8KPW8A6BDI', '811 Smith Rd BackpAQ Labs', 'Purple Air'] // was SSV 2U
        ];

 
var channelKeys =[];
        channelKeys.push({channelNumber:1059654, name:'BackpAQ 1',key:'DZ07N6EQQM0GEUPE',
        fieldList:[{field:1,axis:'O'},{field:2,axis:'O'},{field:3,axis:'O'},{field:4,axis:'O'},{field:5,axis:'O'},{field:6,axis:'T'},{field:7,axis:'H'},{field:8,axis:'O'}]});
        channelKeys.push({channelNumber:1060405, name:'BackpAQ 2',key:'BNY857AMT8UZ8E9X',
        fieldList:[{field:1,axis:'O'},{field:2,axis:'O'},{field:3,axis:'O'},{field:4,axis:'O'},{field:5,axis:'O'},{field:6,axis:'T'},{field:7,axis:'H'},{field:8,axis:'O'}]});
        channelKeys.push({channelNumber:1150280, name:'BackpAQ 3',key:'BMP7BLV51DNQCHQC',
        fieldList:[{field:2,axis:'D'},{field:4,axis:'S'}]});
