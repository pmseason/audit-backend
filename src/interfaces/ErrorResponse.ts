import { MessageResponse } from "../types";


export default interface ErrorResponse extends MessageResponse {
  stack?: string;
}