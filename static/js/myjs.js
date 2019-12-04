/*
function dropItems(idOfDraggedItem,targetId,x,y) {
  var targetObj = document.getElementById(targetId);	// Creating reference to target obj
  var subDivs = targetObj.getElementsByTagName('DIV');	// Number of subdivs
  if (subDivs.length > 0) return;	// Sub divs exists on target, i.e. element already dragged on it. => return from function without doing anything
  var sourceObj = document.getElementById(idOfDraggedItem);	// Creating reference to source, i.e. dragged object
  var numericIdTarget = targetId.replace(/[^0-9]/gi,'')/1;	// Find numeric id of target
  var numericIdSource = idOfDraggedItem.replace(/[^0-9]/gi,'')/1;	// Find numeric id of source
  targetObj.appendChild(sourceObj);	// Append
  var origin = Number(idOfDraggedItem.split("_").pop());
  var target = Number(targetId.split("_").pop());
  post({origin: origin, target: target});
}
var dragDropObj = new DHTMLgoodies_dragDrop();	// Creating drag and drop object
for(var cell=0; cell<=64; cell++) {
  var src = ("piece_").concat(cell.toString());
  var tgt = ("target_").concat(cell.toString());
  if(document.getElementById(src))
    dragDropObj.addSource(src, true);	// Make <div id="box1"> dragable. slide item back into original position after drop
  if(document.getElementById(tgt))
    dragDropObj.addTarget(tgt, 'dropItems'); // Set <div id="leftColumn"> as a drop target. Call function dropItems on drop
}
dragDropObj.init();	// Initizlizing drag and drop object
*/
/* PASTE ABOVE CODE IN SHOW_GAME SCRIPT TO USE DRAG AND DROP INSTEAD OF CLICK */
