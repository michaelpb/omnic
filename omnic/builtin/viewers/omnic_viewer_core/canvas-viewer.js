
class CanvasViewer {
    mount(element) {
        console.log('photo on this element:', element);
        this.canvas = document.createElement('canvas')
        this.canvas.height = element.height;
        this.canvas.width = element.width;
        element.parentNode.insertBefore(element, this.canvas);
        element.parentNode.removeChild(element);
        onCanvasReady(this.canvas);
    }

    onCanvasReady(canvas) {
        console.error('Need to override onCanvasReady', this);
    }
}

module.exports = CanvasViewer;
