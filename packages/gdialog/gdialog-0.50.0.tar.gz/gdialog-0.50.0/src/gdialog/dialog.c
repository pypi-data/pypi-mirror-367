#include <stdio.h>
#include <stdlib.h>
#include <gtk/gtk.h>

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#ifdef WITH_DOC_STRINGS
  #define PyDoc_STR(str) str
#else
  #define PyDoc_STR(str) ""
#endif

/*
  #define Py_RETURN_NONE return Py_None
*/

#define DEFAULT_TITLE "gdialog"
#define DEFAULT_LABEL "Sample Dialog"
#define DEFAULT_MTEXT "Nothing To Do."

void on_close(GtkWidget *widget, gpointer user_data) {
    GtkWidget *dialog = GTK_WIDGET(user_data);
    #if GTK_MAJOR_VERSION >= 3
    gtk_window_close(GTK_WINDOW(dialog));
    #else
    gtk_widget_destroy(GTK_WINDOW(dialog));
    #endif
}

/* gtk_message_dialog */
static PyObject *gdialog(PyObject *self, PyObject *args)
{
      GtkClipboard *clip;
         GtkWidget *gDlg;

         GtkWidget *area;
             GList *children, *l;

        const char *dtext = DEFAULT_MTEXT;
        const char *label = DEFAULT_LABEL;
        const char *title = DEFAULT_TITLE;
               int  dtype = GTK_MESSAGE_INFO;
               int  btype = GTK_BUTTONS_OK;
               int  mflag = 1;
               int  rslts = 0;

    if (!PyArg_ParseTuple(args, "|sssiii", &dtext, &label, &title, &dtype, &btype, &mflag)) {
        return NULL; // 引数解析エラー
    }

    gDlg = gtk_message_dialog_new(
        NULL,
        GTK_DIALOG_MODAL,
        dtype,
        btype,
        "%s", label
    );

    gtk_window_set_skip_taskbar_hint(GTK_WINDOW(gDlg), TRUE);
    gtk_window_set_position(GTK_WINDOW(gDlg), GTK_WIN_POS_CENTER);
    gtk_window_set_title(GTK_WINDOW(gDlg), title);
    if(mflag != 0){
        gtk_message_dialog_format_secondary_markup(GTK_MESSAGE_DIALOG(gDlg), "%s", dtext);
    } else {
        gtk_message_dialog_format_secondary_text(GTK_MESSAGE_DIALOG(gDlg), "%s", dtext);
    }

    #if GTK_MAJOR_VERSION >= 3
    area = gtk_message_dialog_get_message_area(GTK_MESSAGE_DIALOG(gDlg));
    children = gtk_container_get_children(GTK_CONTAINER(area));

    for(l = children; l != NULL; l = g_list_next(l)){
        GtkWidget *child = GTK_WIDGET(l->data);
        if(GTK_IS_LABEL(child)){
            gtk_label_set_selectable(GTK_LABEL(child), TRUE);
            /* if want to target only the first GtkLabel found, break here; */
            // break;
        }
    }
    // GListは解放する必要がある
    g_list_free(children);
    #endif

    gtk_widget_show_all(gDlg);

    rslts = gtk_dialog_run(GTK_DIALOG(gDlg));

    clip = gtk_clipboard_get(GDK_SELECTION_CLIPBOARD);
    gtk_clipboard_store(clip);

    gtk_widget_destroy(gDlg);

    return Py_BuildValue("i", rslts);

}

/* gtk_textview */
static PyObject *gtxview(PyObject *self, PyObject *args)
{
     GtkClipboard *clip;
        GtkWidget *gWin;
        GtkWidget *gDlg;
        GtkWidget *gBox;
        GtkWidget *gLbl;
        GtkWidget *sWin;
        GtkWidget *gTXv;
        GtkWidget *gBtn;
    GtkTextBuffer *gBuf;

        GtkWidget *area;
            GList *children, *l;

        const char *dtext = DEFAULT_MTEXT;
        const char *label = DEFAULT_LABEL;
        const char *title = DEFAULT_TITLE;
              char *mkups;
               int  dtype = GTK_MESSAGE_INFO;
               int  btype = GTK_BUTTONS_OK;
               int  mflag = 1;
               int  rslts = 0;

    if (!PyArg_ParseTuple(args, "|sssiii", &dtext, &label, &title, &dtype, &btype, &mflag)) {
        return NULL; // 引数解析エラー
    }

    gWin = gtk_window_new(GTK_WINDOW_POPUP);
    gDlg = gtk_dialog_new();
    /*gDlg = gtk_dialog_new_with_buttons(
        title,
        GTK_WINDOW(gWin),
        GTK_DIALOG_MODAL,
        "CLOSE"
    );*/

    gtk_window_set_default_size(GTK_WINDOW(gDlg), 256, 384);
    gtk_window_set_skip_taskbar_hint(GTK_WINDOW(gDlg), 0);
    gtk_window_set_position(GTK_WINDOW(gDlg), GTK_WIN_POS_CENTER);
    gtk_window_set_title(GTK_WINDOW(gDlg), title);

    gBox = gtk_dialog_get_content_area(GTK_DIALOG(gDlg));

    gLbl = gtk_label_new(label);
    mkups = g_markup_printf_escaped("<big><b>%s</b></big>", label);
    gtk_label_set_markup(GTK_LABEL(gLbl), mkups);

    #if GTK_MAJOR_VERSION >= 3
    gtk_widget_set_margin_top(gLbl, 6);
    gtk_widget_set_margin_bottom(gLbl, 6);
    #endif

    g_free(mkups);

    gtk_box_pack_start(GTK_BOX(gBox), gLbl, FALSE, FALSE, 0);

    gTXv = gtk_text_view_new();
    gBuf = gtk_text_view_get_buffer(GTK_TEXT_VIEW(gTXv));
    gtk_text_buffer_set_text(gBuf, dtext, strlen(dtext));

    gtk_text_view_set_editable(GTK_TEXT_VIEW(gTXv), TRUE);
    gtk_text_view_set_wrap_mode(GTK_TEXT_VIEW(gTXv), GTK_WRAP_WORD);
    gtk_text_view_set_cursor_visible(GTK_TEXT_VIEW(gTXv), TRUE);
    #if GTK_MAJOR_VERSION >= 3
    gtk_text_view_set_left_margin(GTK_TEXT_VIEW(gTXv), 4);
    gtk_text_view_set_right_margin(GTK_TEXT_VIEW(gTXv), 4);
    gtk_text_view_set_top_margin(GTK_TEXT_VIEW(gTXv), 4);
    gtk_text_view_set_bottom_margin(GTK_TEXT_VIEW(gTXv), 4);
    #endif

    sWin = gtk_scrolled_window_new(NULL, NULL);
    gtk_scrolled_window_set_policy(GTK_SCROLLED_WINDOW(sWin), GTK_POLICY_AUTOMATIC, GTK_POLICY_AUTOMATIC);
    #if GTK_MAJOR_VERSION >= 3
    gtk_widget_set_vexpand(sWin, TRUE);
    gtk_widget_set_hexpand(sWin, FALSE);
    #endif

    gtk_container_add(GTK_CONTAINER(sWin), gTXv);
    gtk_box_pack_start(GTK_BOX(gBox), sWin, TRUE, TRUE, 2);

    gBtn = gtk_button_new_with_label("CLOSE");
    g_signal_connect(gBtn, "clicked", G_CALLBACK(on_close), gDlg);

    gtk_box_pack_start(GTK_BOX(gBox), gBtn, FALSE, FALSE, 0);

    gtk_widget_show_all(gDlg);

    #if GTK_MAJOR_VERSION >=3
    area = gtk_message_dialog_get_message_area(GTK_MESSAGE_DIALOG(gDlg));
    children = gtk_container_get_children(GTK_CONTAINER(area));
    for(l = children; l != NULL; l = g_list_next(l)){
        GtkWidget *child = GTK_WIDGET(l->data);
        if(GTK_IS_LABEL(child)){
            gtk_label_set_selectable(GTK_LABEL(child), TRUE);
            /* if want to target only the first GtkLabel found, break here; */
            // break;
        }
    }
    // GListは解放する必要がある
    g_list_free(children);
    #endif

    rslts = gtk_dialog_run(GTK_DIALOG(gDlg));

    clip = gtk_clipboard_get(GDK_SELECTION_CLIPBOARD);
    gtk_clipboard_store(clip);

    gtk_widget_destroy(gDlg);

    return Py_BuildValue("i", rslts);

}

// モジュール内のメソッド定義
static PyMethodDef dialog_methods[] = {
    {"gdialog", gdialog, METH_VARARGS,
     "A simply GTK dialog."},
    {"gtxview", gtxview, METH_VARARGS,
     "A simply GTK dialog."},
    {NULL, NULL, 0, NULL} // メソッドリストの終端
};

// モジュール定義
static struct PyModuleDef dialog_module = {
    PyModuleDef_HEAD_INIT,
    "dialog",
    "A simply GTK dialog.", 
    -1, // モジュール状態のサイズ (-1 はサブインタープリタごとに状態を持たないことを示す)
    dialog_methods // メソッドリスト
};

// モジュール初期化関数 (Pythonがインポート時に呼び出す)
PyMODINIT_FUNC PyInit_dialog(void)
{

    PyObject* pModule = PyModule_Create(&dialog_module);
    if (pModule == NULL) {
        return NULL;
    }

    // Gtk初期化
    gtk_init(0, NULL);

    // 変数定義例
    // PyObject* は各変数ごとに新しい名前を使い、適切なフォーマット文字列を使用します。
    // PyModule_AddObject に渡すオブジェクトは、PyModule_AddObject が所有権を奪うため、
    // ここで Py_INCREF/Py_DECREF を行う必要はありません。
    // ただし、PyModule_AddObject が失敗した場合に備えて、オブジェクトを解放する処理が必要です。

    //PyObject_SetAttrString(pModule, "my_variable_str", pValue)

    //int c_true_value = 1; // Cのint型
    //PyObject* py_bool_true = PyBool_FromLong(c_true_value);
    // これで py_bool_true は Python の True オブジェクトになります
    int c_false_value = 0;
    PyObject* py_bool_false = PyBool_FromLong(c_false_value);
    // これで py_bool_false は Python の False オブジェクトになります

    if (PyModule_AddObject(pModule, "GTK_MARKUP", py_bool_false) < 0) {
        Py_DECREF(py_bool_false); // 失敗したらオブジェクトを解放
        Py_DECREF(pModule);
        return NULL;
    }
    // py_bool の参照はPyModule_AddObjectが奪ったため、ここではPy_DECREFは不要

    /* Icon */
    PyObject* pGtkMessageInfo = Py_BuildValue("i", 0);
    if (pGtkMessageInfo == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_MESSAGE_INFO", pGtkMessageInfo) < 0) { Py_DECREF(pGtkMessageInfo); Py_DECREF(pModule); return NULL; }

    PyObject* pGtkMessageWarning = Py_BuildValue("i", 1);
    if (pGtkMessageWarning == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_MESSAGE_WARNING", pGtkMessageWarning) < 0) { Py_DECREF(pGtkMessageWarning); Py_DECREF(pModule); return NULL; }

    PyObject* pGtkMessageQuestion = Py_BuildValue("i", 2);
    if (pGtkMessageQuestion == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_MESSAGE_QUESTION", pGtkMessageQuestion) < 0) { Py_DECREF(pGtkMessageQuestion); Py_DECREF(pModule); return NULL; }

    PyObject* pGtkMessageError = Py_BuildValue("i", 3);
    if (pGtkMessageError == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_MESSAGE_ERROR", pGtkMessageError) < 0) { Py_DECREF(pGtkMessageError); Py_DECREF(pModule); return NULL; }

    PyObject* pGtkMessageOther = Py_BuildValue("i", 4);
    if (pGtkMessageOther == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_MESSAGE_OTHER", pGtkMessageOther) < 0) { Py_DECREF(pGtkMessageOther); Py_DECREF(pModule); return NULL; }

    /* Button */
    PyObject* pGtkButtonsNone = Py_BuildValue("i", 0);
    if (pGtkButtonsNone == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_BUTTONS_NONE", pGtkButtonsNone) < 0) { Py_DECREF(pGtkButtonsNone); Py_DECREF(pModule); return NULL; }

    PyObject* pGtkButtonsOk = Py_BuildValue("i", 1);
    if (pGtkButtonsOk == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_BUTTONS_OK", pGtkButtonsOk) < 0) { Py_DECREF(pGtkButtonsOk); Py_DECREF(pModule); return NULL; }

    PyObject* pGtkButtonsClose = Py_BuildValue("i", 2);
    if (pGtkButtonsClose == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_BUTTONS_CLOSE", pGtkButtonsClose) < 0) { Py_DECREF(pGtkButtonsClose); Py_DECREF(pModule); return NULL; }

    PyObject* pGtkButtonsCancel = Py_BuildValue("i", 3);
    if (pGtkButtonsCancel == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_BUTTONS_CANCEL", pGtkButtonsCancel) < 0) { Py_DECREF(pGtkButtonsCancel); Py_DECREF(pModule); return NULL; }

    PyObject* pGtkButtonsYesNo = Py_BuildValue("i", 4);
    if (pGtkButtonsYesNo == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_BUTTONS_YES_NO", pGtkButtonsYesNo) < 0) { Py_DECREF(pGtkButtonsYesNo); Py_DECREF(pModule); return NULL; }

    PyObject* pGtkButtonsOkCancel = Py_BuildValue("i", 5);
    if (pGtkButtonsOkCancel == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_BUTTONS_OK_CANCEL", pGtkButtonsOkCancel) < 0) { Py_DECREF(pGtkButtonsOkCancel); Py_DECREF(pModule); return NULL; }

    /* Button */
    PyObject* pGtkResponseNone = Py_BuildValue("i", -1);
    if (pGtkResponseNone == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_RESPONSE_NONE", pGtkResponseNone) < 0) { Py_DECREF(pGtkResponseNone); Py_DECREF(pModule); return NULL; }

    PyObject* pGtkResponseReject = Py_BuildValue("i", -2);
    if (pGtkResponseReject == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_RESPONSE_REJECT", pGtkResponseReject) < 0) { Py_DECREF(pGtkResponseReject); Py_DECREF(pModule); return NULL; }

    PyObject* pGtkResponseAccept = Py_BuildValue("i", -3);
    if (pGtkResponseAccept == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_RESPONSE_ACCEPT", pGtkResponseAccept) < 0) { Py_DECREF(pGtkResponseAccept); Py_DECREF(pModule); return NULL; }

    PyObject* pGtkResponseDeleteEvent = Py_BuildValue("i", -4);
    if (pGtkResponseDeleteEvent == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_RESPONSE_DELETE_EVENT", pGtkResponseDeleteEvent) < 0) { Py_DECREF(pGtkResponseDeleteEvent); Py_DECREF(pModule); return NULL; }

    PyObject* pGtkResponseOk = Py_BuildValue("i", -5);
    if (pGtkResponseOk == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_RESPONSE_OK", pGtkResponseOk) < 0) { Py_DECREF(pGtkResponseOk); Py_DECREF(pModule); return NULL; }

    PyObject* pGtkResponseCancel = Py_BuildValue("i", -6);
    if (pGtkResponseCancel == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_RESPONSE_CANCEL", pGtkResponseCancel) < 0) { Py_DECREF(pGtkResponseCancel); Py_DECREF(pModule); return NULL; }

    PyObject* pGtkResponseClose = Py_BuildValue("i", -7);
    if (pGtkResponseClose == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_RESPONSE_CLOSE", pGtkResponseClose) < 0) { Py_DECREF(pGtkResponseClose); Py_DECREF(pModule); return NULL; }

    PyObject* pGtkResponseYes = Py_BuildValue("i", -8);
    if (pGtkResponseYes == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_RESPONSE_YES", pGtkResponseYes) < 0) { Py_DECREF(pGtkResponseYes); Py_DECREF(pModule); return NULL; }

    PyObject* pGtkResponseNo = Py_BuildValue("i", -9);
    if (pGtkResponseNo == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_RESPONSE_NO", pGtkResponseNo) < 0) { Py_DECREF(pGtkResponseNo); Py_DECREF(pModule); return NULL; }

    PyObject* pGtkResponseApply = Py_BuildValue("i", -10);
    if (pGtkResponseApply == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_RESPONSE_APPLY", pGtkResponseApply) < 0) { Py_DECREF(pGtkResponseApply); Py_DECREF(pModule); return NULL; }

    PyObject* pGtkResponseOkHelp = Py_BuildValue("i", -11);
    if (pGtkResponseOkHelp == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "GTK_RESPONSE_HELP", pGtkResponseOkHelp) < 0) { Py_DECREF(pGtkResponseOkHelp); Py_DECREF(pModule); return NULL; }

    /* Hello */
    PyObject* pString = Py_BuildValue("s", "Hello from C!");
    if (pString == NULL) { Py_DECREF(pModule); return NULL; }
    if (PyModule_AddObject(pModule, "test_string", pString) < 0) {
        Py_DECREF(pString); // 失敗したらオブジェクトを解放
        Py_DECREF(pModule);
        return NULL;
    }

    return pModule; // 正しく作成したモジュールを返す

}
