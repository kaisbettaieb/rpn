import numbers
import typing
import uuid

from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="RPN API", version="1.0")

op_router = APIRouter(prefix="/rpn/op")

OPERATIONS = ["+", "-", "*", "/"]


class Stack(BaseModel):
    pile: typing.List


app.stacks = {}


@op_router.get("")
def list_all_the_operand():
    return OPERATIONS


@op_router.post("/{op:path}/stack/{stack_id}")
def apply_an_operand_to_a_stack(op: str, stack_id: str):
    if op not in OPERATIONS:
        return JSONResponse(status_code=422, content=f"Operand {op} not supported")
    if stack_id not in app.stacks:
        return JSONResponse(status_code=404, content={"message": "Stack not found"})
    stack = app.stacks[stack_id].copy()
    last_num = stack.pop()
    before_last = stack.pop()
    if not isinstance(last_num, numbers.Number) or not isinstance(before_last, numbers.Number):
        return JSONResponse(status_code=422, content=f"Cannot apply operand {op} on values that are not numbers")
    if op == "+":
        stack.append(before_last + last_num)
    elif op == "*":
        stack.append(before_last * last_num)
    elif op == "-":
        stack.append(before_last - last_num)
    else:
        if last_num == 0:
            return JSONResponse(status_code=422, content=f"Cannot apply operand / on Zero")
        stack.append(before_last / last_num)
    app.stacks[stack_id] = stack
    return JSONResponse(status_code=200, content=app.stacks[stack_id])


stack_router = APIRouter(prefix="/rpn/stack")


@stack_router.post("")
def create_a_new_stack(stack: Stack):
    _id = str(uuid.uuid1())
    app.stacks[_id] = stack.pile
    return JSONResponse(status_code=201, content={"id": _id, "stack": app.stacks[_id]})


@stack_router.get("")
def list_the_available_stacks():
    return app.stacks


@stack_router.delete("/{stack_id}")
def delete_a_stack(stack_id: str):
    if stack_id not in app.stacks:
        return JSONResponse(status_code=404, content={"message": "Stack not found"})
    del app.stacks[stack_id]
    return JSONResponse(status_code=204, content={"message": f"Stack {stack_id} deleted"})


@stack_router.post("/{stack_id}")
def push_a_new_value_to_stack(stack_id: str, value: typing.Any):
    if stack_id not in app.stacks:
        return JSONResponse(status_code=404, content={"message": "Stack not found"})
    app.stacks[stack_id].append(value)
    return JSONResponse(status_code=200, content={"message": f"Value {value} added to stack {stack_id}"})


@stack_router.get("/{stack_id}")
def get_a_stack(stack_id: str):
    if stack_id not in app.stacks:
        return JSONResponse(status_code=404, content={"message": "Stack not found"})
    return JSONResponse(status_code=200, content=app.stacks[stack_id])


app.include_router(op_router)
app.include_router(stack_router)
