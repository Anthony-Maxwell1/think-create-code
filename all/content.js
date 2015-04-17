$(document).ready(function() {
    var content = [
        { title: "ProcessingJS Sandbox",
          src: "https://lti-adx.adelaide.edu.au/think.create.code/static/sandbox.html",
          width: 800,
          height: 1000
        },
        { title: "Code Reordering : Loops and Nesting",
          src: "https://lti-adx.adelaide.edu.au/think.create.code/reorder/code_reorder_3_3_7.html",
          width: 700,
          height: 1050
        },
        { title: "Code Reordering : Making Choices",
          src: "https://lti-adx.adelaide.edu.au/think.create.code/reorder/code_reorder_4_1_4.html",
          width: 750,
          height: 700
        },
        { title: "Code Reordering : Decision Making",
          src: "https://lti-adx.adelaide.edu.au/think.create.code/reorder/code_reorder_4_2_7.html",
          width: 750,
          height: 1350
        },
        { title: "Code Reordering : Shapes, Translating, Rotating, and Scaling",
          src: "https://lti-adx.adelaide.edu.au/think.create.code/reorder/code_reorder_5_3_5.html",
          width: 750,
          height: 700
        }
    ];

    CourseUnits.show(content, 'Think.Create.Code : Interactives');
});
