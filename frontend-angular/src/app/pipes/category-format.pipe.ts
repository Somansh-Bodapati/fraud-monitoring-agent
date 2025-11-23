import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
    name: 'categoryFormat'
})
export class CategoryFormatPipe implements PipeTransform {
    transform(value: string): string {
        if (!value) return '';

        // Convert SNAKE_CASE to Title Case
        return value
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
            .join(' ');
    }
}
