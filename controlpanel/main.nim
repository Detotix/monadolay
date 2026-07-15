import x11/[x, xlib]
import std/posix

type Callback = proc(data: cstring) {.cdecl.}

var cb: Callback


proc worker() =
  let display = XOpenDisplay(nil)
  if display == nil:
    quit("Kann Display nicht öffnen!", 1)

  let screen = XDefaultScreen(display)
  let rootWin = XRootWindow(display, screen)

  let window = XCreateSimpleWindow(
    display, rootWin, 
    10, 10, 320, 240, 1, 
    XBlackPixel(display, screen), 
    XWhitePixel(display, screen)
  )

  discard XSelectInput(display, window, ExposureMask or ButtonPressMask)
  discard XMapWindow(display, window)

  let gc = XCreateGC(display, window, 0, nil)
  discard XSetForeground(display, gc, XBlackPixel(display, screen))

  var event: XEvent
  var clicks = 0

  proc draw() =
    discard XClearWindow(display, window)
    let text = "Clicks: " & $clicks
    cb(text)
    discard XDrawString(display, window, gc, 60, 110, text.cstring, text.len.int32)


  while true:
    discard XNextEvent(display, addr event)

    case event.theType
    of Expose:

      draw()
    of ButtonPress:

      clicks += 1
      draw()
    else:
      discard

  discard XFreeGC(display, gc)
  discard XCloseDisplay(display)

proc start_worker(callback: Callback) {.exportc, dynlib, used.} =
  cb = callback
  worker()
